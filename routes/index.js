const express = require('express');
const router = express.Router();
const neo4j = require('neo4j-driver')

const driver = neo4j.driver('bolt://3.87.72.8:7687',
                  neo4j.auth.basic('neo4j', 'cardboard-properties-beaches'), 
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

module.exports = router;
