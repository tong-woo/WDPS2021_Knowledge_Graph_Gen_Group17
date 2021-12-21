const express = require('express');
var path = require('path');
const router = express.Router();
const neo4j = require('neo4j-driver');
const multer = require("multer");
const {spawn} = require('child_process');

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, path.join(__dirname, '..', 'pipeline', 'books'))
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '.txt'
    cb(null, file.fieldname + '-' + uniqueSuffix)
  }
});
const upload = multer({ storage: storage });

const driver = neo4j.driver(process.env.NEO_HOST || 'bolt://3.87.72.8:7687',
                  neo4j.auth.basic(
                    process.env.NEO_USER || 'neo4j', 
                    process.env.NEO_PASS || 'cardboard-properties-beaches'
                  ), 
                  {/* encrypted: 'ENCRYPTION_OFF' */});

const session = driver.session({database:"neo4j"});

/* GET home page. */
router.get('/', (req, res, next) => {
  res.render('index', {});
});

router.get('/query', (req, res, next) => {
  // QUERY NEO4J for books data
  query = `
    MATCH (n)
    RETURN DISTINCT n.book as books
  `
  session.run(query, {}).then((result) => {
    let books = []
    result.records.forEach((record) => {
      books.push(record.get('books'))
    });
    console.log(books);
    return res.render('query', {
      books
    });
  })
  .catch((error) => {
    console.error(error);
    console.log(error);
    return res.render('error', { error, message: 'Error' })
  });
})

router.get('/query/book/', (req, res, next) => {
  let bookId = req.query.bookId;
  // QUERY NEO4J for bookId data
  const query = `  
      MATCH (n)-->(rel)
      WHERE n.book = "${bookId}"
      RETURN count(rel) as relationships, count(DISTINCT n) as entities
  `;

  session.run(query, {}).then((result) => {
    let relationships, entities;
    result.records.forEach((record) => {
      relationships = record.get('relationships');
      entities = record.get('entities')
    });
    return res.render('book', {
      bookId,
      numEntities: entities,
      numRelationships: relationships
    });
  })
  .catch((error) => {
    console.error(error);
    return res.render('error', { error, message: 'Error' })
  });
})

router.get('/query/entity/', function(req, res, next){
  let {
    bookId,
    entityId
  } = req.query;

  // QUERY NEO4J for entityId relationships
  const query = `  
    MATCH (p {pid: ${entityId}})-[r]->(rel)
    WHERE p.book = "${bookId}"
    RETURN r, rel, p
  `;

  session.run(query, {}).then((result) => {
    let relationships = [];
    let searchEntity;
    result.records.forEach((record) => {
      let r = record.get('r');
      let entity = record.get('rel');
      searchEntity = record.get('p');
      relationships.push({
        ...entity,
        type: r.type,
      });
    });
    return res.render('entity', {
      bookId, 
      entityId, 
      relationships,
      searchEntity
    })
  })
  .catch((error) => {
    console.error(error);
    return res.render('error', { error, message: 'Error' })
  });
})

router.get('/query/book/graph', function(req, res, next) {
  let {
    bookId
  } = req.query;

  // QUERY NEO4J for entityId relationships
  const query = `  
    MATCH (n)-[r]->(rel)
    WHERE n.book = "${bookId}"
    RETURN DISTINCT(r), rel, n
  `;

  session.run(query, {}).then((result) => {
    let relationships = [];
    result.records.forEach((record) => {
      let r = record.get('r');
      let entity = record.get('rel');
      let searchEntity = record.get('n');
      relationships.push({
        source: entity,
        type: r.type,
        target: searchEntity
      });
    });
    return res.status(200).json({
      relationships
    })
  })
  .catch((error) => {
    console.error(error);
    return res.status(500).json(error)
  });  
})

router.get('/query/search/', function(req, res, next){
  let {
    bookId,
    q
  } = req.query;

  const params = {limit: "10"};
  // QUERY NEO4J for bookId - entityId relationships

  const query = `  
    MATCH (p)
    WHERE 
      p.book = "${bookId}" AND
      p.name =~ "(?i).*${q}.*"
    RETURN p
  `;

  session.run(query, params).then((result) => {
    let queryResponse = [];
    result.records.forEach((record) => {
      let p = record.get('p');
      queryResponse.push({
        ...p
      });
    });
    return res.status(200).json({ response: queryResponse })
  })
  .catch((error) => {
    console.error(error);
    return res.status(500).json(error)
  });
})

router.post("/uploadFile", upload.single("myFile"), (req, res, next) => { // myFile should be the same value as used in HTML name attribute of input
  const file = req.file; // We get the file in req.file
  const bookName = req.body.bookName;
  if (!file) { // in case we do not get a file we return
    const error = new Error("Please upload a file");
    error.httpStatusCode = 400;
    return next(error);
  }

  if (!bookName){
    const error = new Error("Please enter a book name");
    error.httpStatusCode = 400;
    return next(error);
  }

  const script_path = path.join(__dirname, '..', 'pipeline', 'pipeline.py');
  const file_path = path.join(__dirname, '..', 'pipeline', 'books', file.filename);
  console.log(file_path);
  const python = spawn('python', [script_path, file_path, bookName]);
  python.on('close', (code) => {
    console.log('Finish!', code);
    // send data to browser
    res.redirect('/query')
  });
});


module.exports = router;
