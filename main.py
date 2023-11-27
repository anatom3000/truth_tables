import itertools

from abc import ABC, abstractmethod
from dataclasses import dataclass


class Tokenizer:
    def __init__(self, text: str):
        self.text = text
        self.index = 0
        self.tokens = []

    def char(self):
        return self.text[self.index]

    def tokenize(self):
        while self.index < len(self.text):
            char = self.char()
            if char in ' \t\n':
                self.index += 1
            elif char in 'abcdefghijklmnopqrstuvwxyz':
                self.variable()
            elif char in '()&+|~':
                self.tokens.append((char, ""))
                self.index += 1
            elif char == '=':
                self.index += 1
                assert self.char() == '>', f"expected `>` of `=>`, found `{self.char()}`"
                self.index += 1
                self.tokens.append(("=>", ""))
            elif char == '<':
                self.index += 1
                assert self.char() == '=', f"expected `=` of `<=>`, found `{self.char()}`"
                self.index += 1
                assert self.char() == '>', f"expected `>` of `<=>`, found `{self.char()}`"
                self.index += 1
                self.tokens.append(("<=>", ""))
            else:
                assert False, f"unkonwn character `{char}`"

    def variable(self):
        var = ""
        while self.index < len(self.text) and self.char() in 'abcdefghijklmnopqrstuvwxyz':
            var += self.char()
            self.index += 1

        self.tokens.append(("variable", var))


class Expression(ABC):
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def vars(self) -> set[str]:
        pass

    @abstractmethod
    def evaluate(self, env: dict[str, bool]) -> bool:
        pass


class BinOp(Expression, ABC):
    name: str

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def __str__(self):
        # return f"{self.__class__.__name__}{self.name, self.left, self.right}"
        return f"({self.left} {self.name} {self.right})"

    __repr__ = __str__

    def vars(self) -> set[str]:
        return self.left.vars() | self.right.vars()

    @abstractmethod
    def evaluate(self, env: dict[str, bool]) -> bool:
        pass


class And(BinOp):
    name = '&'

    def evaluate(self, env: dict[str, bool]) -> bool:
        return self.left.evaluate(env) and self.right.evaluate(env)


class Or(BinOp):
    name = '+'

    def evaluate(self, env: dict[str, bool]) -> bool:
        return self.left.evaluate(env) or self.right.evaluate(env)


class Nand(BinOp):
    name = '|'

    def evaluate(self, env: dict[str, bool]) -> bool:
        return not (self.left.evaluate(env) and self.right.evaluate(env))


class Implies(BinOp):
    name = '=>'

    def evaluate(self, env: dict[str, bool]) -> bool:
        return (not self.left.evaluate(env)) or self.right.evaluate(env)


class Equiv(BinOp):
    name = '<=>'

    def evaluate(self, env: dict[str, bool]) -> bool:
        return self.left.evaluate(env) == self.right.evaluate(env)


@dataclass
class Not(Expression):
    arg: Expression

    def __str__(self):
        return f"~{self.arg}"

    def vars(self) -> set[str]:
        return self.arg.vars()

    def evaluate(self, env: dict[str, bool]) -> bool:
        return not self.arg.evaluate(env)


@dataclass
class Variable(Expression):
    name: str

    def __str__(self):
        return self.name

    def vars(self) -> set[str]:
        return set([self.name])

    def evaluate(self, env: dict[str, bool]) -> bool:
        assert self.name in env.keys(), f"cannot evaluate variable `{self.name}`"
        return env[self.name]


class Parser:
    def __init__(self, tokens: (str, str)):
        self.tokens = tokens
        self.index = 0

    def debug(self):
        return

        if self.index < len(self.tokens):
            print(f"DUMP\n\t{self.tokens = }\n\t{self.index = }\n\ttoken={self.tokens[self.index]}")
        else:
            print(f"DUMP\n\t{self.tokens = }\n\t{self.index = }\n\ttoken=None")

    def token(self):
        return self.tokens[self.index]

    def equiv(self) -> Expression:
        self.debug()

        expr = self.implic()

        self.debug()

        while self.index < len(self.tokens) and self.token()[0] == '<=>':
            self.debug()
            self.index += 1
            expr = Equiv(expr, self.implic())

        return expr

    def implic(self) -> Expression:
        self.debug()

        expr = self.nand()

        while self.index < len(self.tokens) and self.token()[0] == '=>':
            self.index += 1
            expr = Implies(expr, self.nand())

        return expr

    def nand(self) -> Expression:
        self.debug()

        expr = self.orr()

        while self.index < len(self.tokens) and self.token()[0] == '|':
            self.index += 1
            expr = Nand(expr, self.orr())

        return expr

    def orr(self) -> Expression:
        self.debug()

        expr = self.andd()

        while self.index < len(self.tokens) and self.token()[0] == '+':
            self.index += 1
            expr = Or(expr, self.andd())

        return expr

    def andd(self) -> Expression:
        self.debug()

        expr = self.nott()

        while self.index < len(self.tokens) and self.token()[0] == '&':
            self.index += 1
            expr = And(expr, self.nott())

        return expr

    def nott(self) -> Expression:
        self.debug()

        if self.token()[0] == '~':
            self.index += 1
            return Not(self.nott())
        else:
            return self.unit()

    def unit(self) -> Expression:
        self.debug()

        if self.token()[0] == '(':
            self.index += 1
            expr = self.equiv()
            assert self.token()[0] == ')', "missing closed paren"
            self.index += 1
            return expr
        elif self.token()[0] == 'variable':
            expr = Variable(self.token()[1])
            self.index += 1
            return expr
        else:
            assert False, f"expected expression, found {self.token()}"


text = input("> ")
tok = Tokenizer(text)
tok.tokenize()
par = Parser(tok.tokens)

expr = par.equiv()
vars = sorted(list(expr.vars()))
print("| " + " | ".join(vars) + " | - |")
for vs in itertools.product((True, False), repeat=len(vars)):
    env = {var: v for var, v in zip(vars, vs)}
    result = expr.evaluate(env)
    print("| " + " | ".join([str(int(env[var])) for var in vars]) + f" | {int(result)} |")

