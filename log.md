💾 메모리 최적화: 모듈화 완료
데이터베이스 초기화 실패: error: duplicate key value violates unique constraint "pg_type_typname_nsp_index"
    at C:\Users\gmdqn\signalcraft\node_modules\pg\lib\client.js:545:17
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async DatabaseService.createTables (C:\Users\gmdqn\signalcraft\services\database_service.js:44:13)
    at async DatabaseService.init (C:\Users\gmdqn\signalcraft\services\database_service.js:30:13) {
  length: 245,
  severity: 'ERROR',
  code: '23505',
  detail: 'Key (typname, typnamespace)=(users, 2200) already exists.',
  hint: undefined,
  position: undefined,
  internalPosition: undefined,
  internalQuery: undefined,
  where: undefined,
  schema: 'pg_catalog',
  table: 'pg_type',
  column: undefined,
  dataType: undefined,
  constraint: 'pg_type_typname_nsp_index',
  file: 'nbtinsert.c',
  line: '666',
  routine: '_bt_check_unique'
}
데이터베이스 초기화 실패: error: relation "users" already exists
    at C:\Users\gmdqn\signalcraft\node_modules\pg\lib\client.js:545:17
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async DatabaseService.createTables (C:\Users\gmdqn\signalcraft\services\database_service.js:44:13)
    at async DatabaseService.init (C:\Users\gmdqn\signalcraft\services\database_service.js:30:13) {
  length: 99,
  severity: 'ERROR',
  code: '42P07',
  detail: undefined,
  hint: undefined,
  position: undefined,
  internalPosition: undefined,
  internalQuery: undefined,
  where: undefined,
  schema: undefined,
  table: undefined,
  column: undefined,
  dataType: undefined,
  constraint: undefined,
  file: 'heap.c',
  line: '1150',
  routine: 'heap_create_with_catalog'
}
데이터베이스 초기화 실패: error: duplicate key value violates unique constraint "pg_type_typname_nsp_index"
    at C:\Users\gmdqn\signalcraft\node_modules\pg\lib\client.js:545:17
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async DatabaseService.createTables (C:\Users\gmdqn\signalcraft\services\database_service.js:44:13)
    at async DatabaseService.init (C:\Users\gmdqn\signalcraft\services\database_service.js:30:13) {
  length: 245,
  severity: 'ERROR',
  code: '23505',
  detail: 'Key (typname, typnamespace)=(users, 2200) already exists.',
  hint: undefined,
  position: undefined,
  internalPosition: undefined,
  internalQuery: undefined,
  where: undefined,
  schema: 'pg_catalog',
  table: 'pg_type',
  column: undefined,
  dataType: undefined,
  constraint: 'pg_type_typname_nsp_index',
  file: 'nbtinsert.c',
  line: '666',
  routine: '_bt_check_unique'
}
데이터베이스 초기화 실패: error: duplicate key value violates unique constraint "pg_type_typname_nsp_index"
    at C:\Users\gmdqn\signalcraft\node_modules\pg\lib\client.js:545:17
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async DatabaseService.createTables (C:\Users\gmdqn\signalcraft\services\database_service.js:44:13)
    at async DatabaseService.init (C:\Users\gmdqn\signalcraft\services\database_service.js:30:13) {
  length: 245,
  severity: 'ERROR',
  code: '23505',
  detail: 'Key (typname, typnamespace)=(users, 2200) already exists.',
  hint: undefined,
  position: undefined,
  internalPosition: undefined,
  internalQuery: undefined,
  where: undefined,
  schema: 'pg_catalog',
  table: 'pg_type',
  column: undefined,
  dataType: undefined,
  constraint: 'pg_type_typname_nsp_index',
  file: 'nbtinsert.c',
  line: '666',
  routine: '_bt_check_unique'
}
🗄️ PostgreSQL 데이터베이스 초기화 완료
