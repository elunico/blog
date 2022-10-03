%tags terminal, programming, programming languages, macOS, electron, javascript, native apps, design, ui
%summary Thoughts on choosing a terminal emulator for the Mac and the nature of telemtry in software
%date 2022-10-03T18:25:36.246542

# Terminal Emulators

Thanks to a sponsorship on [Daring Fireball](https://daringfireball.net/), I have recently been using [Warp](https://www.warp.dev/) and liking it a lot. Warp is a new terminal emulator written in
Rust. What drew me to it most was the full-native experience that it claimed to provide. Like many, I am no stranger to 
Electron apps nor to the bloat and issues that they provide. As a side note, I feel like there is this great emphasis 
lately to make apps "feel the same" across platforms. While I recognize some utility to this and I understand that it may
be some people's preference, I have always preferred making apps that well suited to the native and expected design 
of their platforms. I understand that this creates far more development work so I am sympathetic to these "write
for the web, run on everything" frameworks. Still, I cannot help but miss the days of fully-native, platform-specific 
apps. 

## A brief tangent

I remember this being a particular draw of the Mac in the late 00s to early 10s. Mac Apps always had such 
rich (skeumorphic, sometimes to a fault) designs that fully integrated into the Mac design language and ecosystem.
Programs like the iWork suite, Things, OmniFocus, 1Password, Banktivity, TextMate, BBEdit, and so forth. They
supported Mac things like sheets, proxies, AppleScript, drag and drop, the system font panel and color panel—They felt at home on the
Mac. Now-a-days [everything is just a webpage](https://www.electronjs.org/apps) and nothing works how you expect it because it's all secretly living this double
life as JavaScript. 

While I did praise the Mac at one time for offering this, even Apple is not exempt from this trend
as they seem to be focusing on anything but the Mac lately. The apps have also gotten to look a lot more similar across
platforms at the cost of intuition and features (see iWork c. 2013 to now). Apple has always been good at making software 
and hardware seamless and jamming iPhone and iPad apps onto a Mac completely trash the harmony between hardware and software
and the consistency and reliability that was at once a trademark of the Mac.

What's more even some of my favorite apps like [1Password](https://www.electronjs.org/apps) have now become electron apps 

## Back on Track
Anyway, this is supposed to be about terminals. I was drawn to Warp because they are a fully native terminal for the Mac. 
Many popular terminals are not native—most immediately [hyper.js](https://hyper.is/) comes to mind. Electron apps are not
necessarily bad (I use VS Code every day among others), but I was intrigued to see a full-fat native app come out and 
one written in Rust no less. I was excited to try it.

### Pros and Cons of Warp

To start I should mention, aside from being native and fast and a few other adjectives (see above for the link),
Warp does brand itself as a collaborative terminal. This 
is—to my knowledge—a fairly unique idea, but, as I will explain, as others have pointed out, and as you can imagine, 
this leads to some interesting design choices that many people—especially in software—might be troubled by.

#### Cons
Immediately, the first major con of Warp is the telemetry. Warp **requires** a sign in with Email, Google or Github to be used.
This is obviously concerning for a number of reasons. What's worse is, while Warp is in beta, telemtry (of which there is 
[quite a lot](https://docs.warp.dev/getting-started/privacy#exhaustive-telemetry-table)) is **not** optional. I think
this would bother many people but none more so—perhaps—than people who make software or otherwise use a terminal enough
to replace their system default. There is really no way to justify this in my opinion, and I use the terminal despite this, 
knowing it is really not excusable. 

Another issue that I have with the terminal is that some things about it are a little buggy. This is unacceptable in a 
fully baked terminal release as I believe terminal access is far too critical and fundamental to leave to chance bugs, 
however, Warp is not a fully baked terminal release, it is a beta, so this is understandable—at least for now. I tend 
to run into the terminal being very slow on input most often. Another bug I see involving rendering, where my cursor and 
the screen, and the actual text all disagree on what is going on. This only seems to occur if I open a program like
nvim or similar and only rarely even then. 

I also find it nearly impossible to type into the current session if I create 
or start a process in the background that is producing output. This is made worse by the entire terminal seeming to 
lock up if a tab is producing large amounts of output while I am in a different tab.

Warp also only supports [a couple of shells](https://docs.warp.dev/getting-started/using-warp-with-shells). This is 
not as a huge deal to me personally because I don't and have not met anyone who doesn't use bash, zsh, or fish, but 
if you do, you will not like Warp unless 1) they add more supported shells or 2) you feel like switching.

#### Pros
Still, there is a lot I like about Warp. It's most captivating feature, in my opinion, is the [text editor](https://docs.warp.dev/features/the-input-editor) capabilities 
of the input area. Warp allows you to type into the terminal as if it were a text editor. Complete with selection, 
word and line jumps with hotkeys, multiple lines, and even multiple cursors. This is very powerful for many uses and 
I like it a lot

Another excellent feature is how it treats [previous commands and their output as single units rather than lines of text](https://docs.warp.dev/features/blocks). 
Anyone who knows me knows I am a *HUGE* fan of UNIX and the UNIX philosophy, but there is always wiggle room in such a 
broad foundation. So, while I respect the idea of "everything is a stream of text" there is no doubt that—from a UX 
perspective—the blocks make the terminal much more human-friendly. They allow you to operate on commands and their output, 
saving, copying, pasting, etc. You can copy commands, their output, both, you can scroll around block by block, etc. 

Warp also offers [autocomplete](https://docs.warp.dev/features/autosuggestions) based on your history and commands
and it has [completions for common commands](https://docs.warp.dev/features/completions) that can fill in parameters or 
arguments and can offer even offer [documentation](https://docs.warp.dev/features/command-inspector) for options and switches. 

#### More Cons
Unfortunately, now that I have explained the cool part about blocks and autocomplete, I must return to the bad parts 
of Warp. 

For one thing, the [blocks can be "permalinked."](https://docs.warp.dev/features/blocks/block-actions) You can take, literally, any command that you run and create a permanent
image of that command and its output, published to the internet by warp, and accessible to anyone with the link.
You do have to deliberately choose a block, click the menu, and choose permalink, but 1) there is no clear indication
that this action will publish your command to the internet (there is some language around sharing, but it could export an image
and it is not at all clear to me that this will publish something) 2) the fact that this is possible at all is troubling
to many people. You can also read more about their privacy [here](https://www.warp.dev/privacy) and [here](https://docs.warp.dev/getting-started/privacy)

Now here is where I stop and say, remember that Warp's whole Thing is that it is the Collaborative Terminal, so this 
makes sense in light of that. Also, to be fair, they are [aggresively marketing](https://docs.warp.dev/features/blocks/block-actions) their own "users have control—its opt-in"
angle. Which, it seems, it is. Warp being closed source for the time being means we cannot **know** it is, but they 
at least seem to be making a point of saying it is. Again, to be fair, if you are trying to build a company on a new idea, 
closed source is probably necessary, and they have said [they plan to open source](https://docs.warp.dev/features/blocks/block-actions) **part** of their code
But I think this will lead many people to ask "Do I really need a collaborative terminal if this is what it costs?"

The other thing Warp offers is AI Command Suggestions. They can take an English description of an action and turn it
into one or more commands using AI. This is, frankly, the least concerning to me. While I am sending their servers data, 
I am only sending an English description of what I want and, presumably, not putting in my passwords to the AI prompt. 
I am sure Github knows more about my code than this AI command generator, so while this is less concerning to me, 
it is still a use of my data, that is certainly worth mentioning. Warp [does say](https://docs.warp.dev/features/ai-command-search)
that commands are not sent or monitored and that this is a strictly opt-in feature—if you don't like it just don't use
AI command search. 

### Features not Covered
Warp also has something called [workflows](https://docs.warp.dev/features/workflows) which I have not really explored. 
I am quite comfortable with my functions and aliases, though I get the sense that workflows are "better" somehow and 
will also play quite a big role in that whole "collaboration" thing I mentioned earlier. Still, I'm not really using
Warp because I want to collaborate on the Terminal, I am using it because it is fast, native, and aesthetically very 
pleasing. 

## Competitors
I have been a faithful and long-time user of the built-in macOS terminal (from 2011 back when it was still called
the Mac OS X Terminal). I have nearly always found this sufficient for my needs. I have vollied, periodically, 
back and forth between using [iTerm 2](https://iterm2.com/) and the built-in Terminal, but I never really find myself taking much advantage
of the litany of extra features iTerm offers. Still, when I find a beta bug in Warp, iTerm 2 is what I turn to. 
What brings me back to warp though is the blocks and the text-editing input and the fact that it just looks and feels nicer
adn slicker than iTerm 2. I am excited, but also concerned about the future of Warp and its telemetry and collaboration.

## Conclusion
Warp is a very nice, very beautiful, fun to use, and fairly innovative Terminal, that I enjoy. However, its approach to 
"sharing" and data collection should give anyone who works with any kind of software (read: everyone) pause before using
especially for or at work or for mission critical or otherwise confidential tasks. Its status a beta should re-inforce the 
idea that this is yet to be a production ready terminal. 

## Discaimer
I am in no way affiliated with Warp, its promotion, or development. I have a lot of respect and admiration for the team 
behind it as I think it is not only unique but also quite useful and I am using it completely on my own. Everything
stated in this article is my own opinion and does not reflect the thoughts or opinions of anyone but myself. 