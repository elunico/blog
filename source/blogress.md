%tags update, meta, blog, programming, python, web, ui, design, css
%summary An update on the progress of my roll-your-own-blog blog
%date 2022-09-27T17:51:05.900902

# blogress

The roll-your-own-blog blog has gotten off to a voracious start. In only 2 days, I am quite satisfied with the progress that
I have made. Obviously it is still far from being anything more than a 2-day side-project version of re-inventing the wheel.
I am not trying to claim to be making the next Blogspot here, but I am having fun.

## Issues and Debt

One thing that I know just based on feel, but also based on looking at the code that I wrote, is that things are fairly
tightly coupled. My build code could do with a lot more modularization and genericization. Extending things further or for
other uses would definitely need quite a refactoring job. I am trying to keep things separated at least at the procedure level,
but still there is room for improvment. The build system is done in Python, and—while my relationship with Python can best be
described as "frenemies"—Python is good for expressive and concise code. When I write Python, I feel like I can take a complex
thought and express easily in one line...until of course I have to write something like a for...else loop. Anyway, the
issue I seem to have with the code is often the issue I have with Python code which is that it is so expressive and concise
that I often start writing without much regard for custom data types, class hierarchies, or modules. I hope to remedy this in
time. At this point I am quite satisfied with the functionality of the blog for the amount of time that I have been working on
it so now might be a good time to take a step back and focus on design and organization.

Another place I would like to improve is the `stylesheet.css` file. This file is currently the one and only global
CSS file that applies to all classes. Obviously this is nice becasue it keeps design consistent, but it also is not
ideal due to the cascade and name collisions. I would like to redo things to tie the name of the stylesheet to the
HTML that it should apply to. I already have a mechanism for including HTML parts into larger HTML files or templates,
and I think this approach might work for the CSS. On a more...ambitious level, I would like to add a way of not only
modularizing the CSS but possibly parsing the HTML to mangle CSS selectors to be unique to the file that they belong UNLESS
indicated to be universal. This would require quite a bit of tooling not only for the parsing, but the scoping of CSS selectors
as well as the organziation of code and files. For now, I imagine the single stylesheet will suffice, and I would rather tackle
the Python code refactor before dealing with the CSS. *I have very, very briefly considered another style provider like SCSS or
SASS, but—in keeping with the roll-your-own aspect of the blog—the more "vanilla" I can keep things that happier I will be.

## Future Plans

Separate from the issues and debt, there are some future plans I have that do not involve addressing any *current* problems.

For one thing, I would like to create a general text search rather than the current ability to only filter by tag. This might be
a bit difficult especially with many, large articles. Further complicating this is the fact that I am hosting the website statically on Github Pages currently, so there is no backend currently for executing efficient searches by database. All work
must be done on the client. Currently, for the size of the blog, this is not an issue, but it may be in the future.

