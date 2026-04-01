# ORM patterns to scan (quick reference)

Use this file when the codebase relies heavily on ORM/query builders, to locate query hotspots and typical performance traps (especially N+1 and over-fetching).

## JavaScript/TypeScript

- **Prisma**: `prisma.<model>.findMany/findFirst/findUnique`, `include`, `select`, `where`, `orderBy`, `take/skip`, `transaction`
- **TypeORM**: `createQueryBuilder`, `.leftJoinAndSelect`, `.innerJoin`, `.relations`, `.find({ relations: ... })`
- **Sequelize**: `Model.findAll/findOne`, `include`, `attributes`, `where`, `limit/offset`
- **Knex**: `knex(...)`, `.select`, `.where`, `.join`, `.orderBy`, `.limit`, `.offset`
- **Mongoose**: `Model.find/findOne/aggregate`, `.populate`, `.select`, `.lean`, `.limit`, `.skip`

## DynamoDB (ORM/ODM + helpers)

### JavaScript/TypeScript

- **AWS SDK v3 + DynamoDBDocumentClient**: `DynamoDBDocumentClient.from(...)`, `docClient.send(new QueryCommand(...))`, `GetCommand/PutCommand/UpdateCommand/DeleteCommand`, `BatchGetCommand/BatchWriteCommand`, `ScanCommand`
- **AWS SDK v2 DocumentClient**: `new AWS.DynamoDB.DocumentClient()`, `.query(...)`, `.scan(...)`, `.get(...)`, `.put(...)`, `.update(...)`, `.batchGet(...)`, `.batchWrite(...)`, `.transactGet(...)`, `.transactWrite(...)`
- **Dynamoose**: `dynamoose.model(...)`, `Model.query(...)`, `Model.scan(...)`, `Model.get(...)`, `Model.batchGet(...)`, `Model.batchPut(...)`
- **ElectroDB**: `new Entity(...)`, `entity.query.<index>(...)`, `entity.get(...)`, `entity.put(...)`, `entity.update(...)`
- **DynamoDB Toolbox / OneTable**: `new Table(...)`, `new Entity(...)`, `table.get/query/scan/update/put(...)`

### Python

- **boto3**: `boto3.client('dynamodb').query/scan/get_item/...`, `boto3.resource('dynamodb').Table(...).query/scan/get_item/...`
- **PynamoDB**: `Model.get(...)`, `Model.query(...)`, `Model.scan(...)`, `Model.batch_get(...)`, `Model.batch_write()`

## Python

- **SQLAlchemy**: `session.query(...)`, `select(...)`, `.join`, `.options(joinedload/selectinload/subqueryload)`, `.limit/.offset`
- **Django ORM**: `Model.objects.filter/get`, `.select_related`, `.prefetch_related`, `.only/.defer`, `.values/.values_list`, `.annotate`, `.iterator`

## Java/Kotlin

- **Hibernate/JPA**: `createQuery`, `CriteriaBuilder`, `@OneToMany/@ManyToOne` lazy loading, `JOIN FETCH`, `EntityGraph`

## MongoDB (ODM/driver)

### JavaScript/TypeScript

- **MongoDB Node driver**: `MongoClient`, `collection.find(...)`, `collection.findOne(...)`, `collection.aggregate(...)`, `collection.updateOne/updateMany(...)`, `collection.bulkWrite(...)`
- **Mongoose**: `Model.find/findOne/aggregate`, `.populate`, `.select`, `.lean`, `.limit`, `.skip`

### Python

- **PyMongo**: `MongoClient`, `collection.find/find_one/aggregate/update_one/update_many(...)`
- **Motor**: `AsyncIOMotorClient`, `collection.find(...)`, `collection.aggregate(...)`
- **MongoEngine**: `Document.objects(...)`, `.only/.exclude`, `.select_related`, `.aggregate(...)`

### Java/Kotlin

- **Spring Data MongoDB**: `MongoTemplate`, `ReactiveMongoTemplate`, `MongoRepository`, `@DBRef` lazy-loading patterns

## Go

- **GORM**: `db.Where/Joins/Preload/Select`, `.Find/First`, `.Limit/.Offset`
- **Ent**: `.Query()`, `.With<edge>()`, `.Select`, `.Limit/.Offset`
