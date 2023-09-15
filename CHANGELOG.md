## 2.3.0 (2023-09-15)

### Fix

- updated code to use lazyfields instead of custom implementation

## 2.1.0 (2023-07-25)

### Feat

- added helpers for new cases and improved envfile reading to support comments and quotes better
- added support for Env.QA
- refactored the code, improved utils and helpers and removed case-insensitive and cacheconfig
- **envconfig**: moved envconfig core functionality to optionalconfig and created envconfig on top of
- **envconfig**: created envconfig which loads env only if expected env matches received

### Fix

- **envconfig**: fixed default validation
- **envconfig**: changed ignore default validation
- **envconfig**: now considers env by relevance
- **config**: now missing is class instead of an object to make better typing
- **envconfig**: changed behavior on get if value is optional
- added py.typed to comply to pep561

### Refactor

- **config**: added support for py3.9

## 1.1.0 (2022-06-30)

### Feat

- **helpers**: added helpers for serialization
- **config**: expanded single file, created tests and helpers
- **initial_commit**: empty

### Fix

- **package**: fixed missing package files on build
- **name**: alterado nome do projeto para fazer upload
