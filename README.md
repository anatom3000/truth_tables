# Truth Table

A simple truth table generator.

### Usage

```
python main.py
```
Note: you can use `rlwrap` to get prompt history :
```
rlwrap python main.py
```

No dependencies are required.

### Examples

```
> a + ~a
| a | - |
| 1 | 1 |
| 0 | 1 |
```

```
> a&b <=> (~a+b)
| a | b | - |
| 1 | 1 | 1 |
| 1 | 0 | 1 |
| 0 | 1 | 0 |
| 0 | 0 | 0 |
```


### Syntax

> Note: listed by decreasing precedences
- not: `~a`
- and: `a + b`
- or: `a + b`
- nand: `a | b`
- implies: `a => b`
- iff: `a <=> b`

Parentheses are supported.

