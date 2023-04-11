%tags python, programming, arguments, convention, style, programming style, programming languages
%summary My issues with Python despite it being a go to language
%date 2022-10-01T20:56:39.479340

# Default Arguments in Python

I have, in the past, described the Python programming language as my frenemy. This is an apt description to me because
I turn to Python a lot and we do good work together. This very blog has a custom build system written entirely in Python.
No language lets me produce results as quickly as Python. It may not be the most convenient for delivery (that goes to the Web
and JavaScript) and it may not be the most performant (take your pick on this one but shout out to Rustaceans) but
when I get an idea in my head I can either find a Python package that does what I want or write something myself really fast.

That being said, so much of what Python does displeases me. Some of it I do understand. The iterator model with global functions
for things like length, filter, reduce, and map, are... ugly—to be frank—but I understand why they are that way. I still think
there are better-looking solutions but considering how dynamic Python's types can be, I get why the design is the way that it is.

All the same, there are things that I just do not understand and also hate a lot all the time.

## Things I Hate a Lot All The Time

I will attempt to order these in order of least egregious to most.

### Assignment

They actually fixed this one in 3.10 adding the walrus operator (`:=`) for assignment expressions, but still
I think they should have done it sooner, because not a lot of places run 3.10 yet.

Unlike, many of the other ones on this list, I do see the justification for not making assignment an expression.
Still, I feel this is a more useful feature than common source of errors and so I would rather have it than not. Happy that we
have finally got it and—to be fair to Python—having both operators is probably the best way to do it.

### Blocks

No Blocks. Why? Why are there no blocks in Python? So much of what I have done would be so much nicer if I could have
anonymous blocks. The fact that you can put a named function (or even class) anywhere is nice, but it is not nice enough.
I want anonymous functions and closures that can be longer than a single expression

### For-else loops

`for-else` loops. This one I do not get at all. Like I know the motivation—I read the thing by Guido Von Rossum, but still
why? As I understand it, the point was to replace labeled breaks—among other things—but to be less confusing and disruptive.
I fail to see, even now, how a `for-else` loop—a thing which has never existed and continues to not exist in any mainstream
language that I know of is more clear than a labeled break; break being something every language has an labels being pretty self-explanatory on their own. This baffles me

### Default Arguments for Collections

This is by far the most egregious example, in my opinion. When you have a function in Python, the default arguments of the
function are—according to [Python Documentation](https://docs.python.org/2/reference/compound_stmts.html#function)—evaluated
once at definition time. The arguments are then saved for the function throughout its life. This results in certain...quirks
when defining a function. For example, if I define a function

```python
def some_fn(arg1, arg2=[]):
    # some function
    ...
```

Every invocation of `some_fn` will use the **exact same list for arg2**. Any collection in this position will do the same be it
`[]`, `list()`, `{}`, `dict()`, or `set()`. While this is well-documented, technically speaking, I find this the worst example
because nothing about using the Python language itself, would indicate this is true. This seems to be a very strange and
unexpected bug in code that uses it, and I have never had a person do this, find out why it was wrong, and not be shocked and appalled by its existence.

I find it especially odd that a language like Python would choose to avoid labeled breaks and assignment expressions in order
to avoid confusion and easy-to-cause bugs, and then implement default arguments in this way.

By the way, the recommended way to do this is

```python
def better_fn(arg1, arg2=None):
    if arg2 is None:
        arg2 = []

    # function body
    ...
```

This is a terrible idiom that removes the implicit type† from the parameter, adds 2 lines of boilerplate cruft to the body of the function and separates the default value (and type) from the argument.

This is easily the most annoying thing about Python, though I will admit it is a very close race between the lack of blocks, `for-else` loops and this default argument nonsense.

_† Yes I know talking about types in Python is Controversial, but many programs and IDEs can track variable types in Python and provide hinting based on their assignment in a program and, often times, this use of None harms the analysis of the program and ability of editors to provide suggestions._

## What Does This Mean for Python

Still, as much as these things greatly irritate me, I still do love Python. It is so easily to use and a lot of the time
it can be fun. While there are many wonderful programming languages, I just enjoy writing Python... most of the time; and I certainly feel fastest when I'm writing Python. The only language that ever feels as fast is maybe JavaScript. But Python
still remains one of my most favorite languages....except when it is isn't.
