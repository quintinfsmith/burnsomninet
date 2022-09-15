# Regex modifications
Regex is supported in searches, however some modifications have been made to make it more useful in the context of all bytes rather than just the human-readable ones.

## Byte Wildcarding
Use a `.` to indicate a wildcard within a byte.

### Examples
This will find all bytes from \x90 to \x9F:
```
find \x9.
```

This can also be done in binary:
```
find \b1001....
```
and doesn't need to be sequential
```
find \b100100.0
```
will match \x90 & \x92

