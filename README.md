## Provider filename checker

This repository helps determine how different online storage providers handle different filenames. Rather than relying 
on fickle documentation, it relies on empirical metrics.

For the initial version, it uploads files through waterbutler and checks the response payload. This allows us to 
simplify code around authentication and credential management, but it means that any errors could be due to the 
waterbutler layer rather than provider-specific rules. 

Future versions will make raw API requests with a custom per-provider abstraction.

## TODO
- [ ] Per provider abstractions without going through Waterbutler
- [ ] Support checking folder vs filename rules (currently not possible via tests- maybe a third "scenario csv" column is in order?)
  - Check in different order (create folder, then file with same name- or vice versa)
- [ ] Fix box provider (unhelpful 400 errors)
