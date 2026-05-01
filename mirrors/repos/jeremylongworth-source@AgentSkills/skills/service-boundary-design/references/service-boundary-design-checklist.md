# Service Boundary Design Checklist

## Boundary Inputs

- Domain responsibilities
- Data ownership
- Team ownership
- Deployment needs
- Latency requirements
- Reliability requirements
- Scaling constraints
- Compliance or isolation needs

## Boundary Review

- Public interface clear
- Owned data clear
- Forbidden dependencies named
- Transaction boundary understood
- Consistency model explicit
- Failure modes identified
- Migration path realistic
- Simpler modular option considered

## Output

- Keep together
- Split module
- Split service
- Add integration boundary
- Defer until scale or ownership evidence appears
