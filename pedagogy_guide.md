# Pedagogy Best Practices
Pedagogy is commonly understood as an approach to teaching.  The "Best Practices" listed below are meant as a guide
to developing Jupyter Notebooks for tutorials.  These tutorials may be self-guided tutorials intended for users to work through
on their own; or tutorials taught by an instructor in a workshop or hackathon environment.

The "Best Practices" draw on ideas from the [Carpentries](https://software-carpentry.org/) and also include some ideas on
content from [divio.com](divio.com) and EarthCube.

### Have a well defined purpose for your notebook
What is the purpose of the tutorial?  Each notebook should have a clear description of what it covers.  Focusing on one task
is better than trying to cover multiple tasks.  See also [Avoid cognitive overload](#avoid_cognitive_load)

Describe the purpose or aim of the notebook as an introduction.  If the aim is to produce a plot, include a PNG of the plot to show
the end result.

### Enumerate learning objectives
List the learning objectives after the notebook description.

### Consider your audience
Are they beginners with no experience of writing code, or are they experienced coders who just want to find the best way to read some data 

### Consider the duration of the tutorial
Try to keep the time required to complete a notebook short.  This speaks to focusing on one task.  Users may give-up or loose interest if notebooks require too much time.
Thirty minutes is a good duration to aim for.

### Consider the aim/objective of the note book
Is the notebook a Tutorial to teach a concept or tool or a How To Guide to show how to perform a task?  Is the notebook intended to be self guided or taught by an instructor in a workshop?
[divio.com](https://documentation.divio.com/structure/) provide a good overview of the differences between Tutorials and How-To Guides; both describe practical steps but Tutorials designed
to allow users to understand concepts, whereas How-To Guides are more problem orientated and designed to solve problems that come up during working.  


###<a name="avoid_cognitive_overload"></a>Avoid cognitive overload by focusing on one main task to complete
Not the only or best guide but useful. https://blog.innerdrive.co.uk/4-ways-to-overcome-cognitive-overload?hs_amp=true
Notebooks should be for a single - short - task.  This avoids cognitive overload.

### Follow best practices for coding but avoid overly complicated code.
Code needs to be understandable rather than efficient.  Avoiding trying to write code as a 'developer'.

Aim to follow best practices for coding but also avoid overly complicated code that obscures the teaching aim.  For example, there is no need to
include code to manage errors and exceptions.  Tutorial code does not need to be efficient but does need to be understandable.

### Avoid long code blocks
If a code block is so long that users cut-and-paste the code or press shift-enter then they are not learning, just copying.  The Carpentries advocate live-coding,
where an instructor types code in real-time, correcting mistakes as the go and describing what they are doing.  This approach helps with pacing and length of content.
While most useful in workshops, thinking of writing code live, even for self-guided tutorials, will help keep coding manageable and cognitive load manageable.

Short code blocks also help break tasks into understandable steps.  Think in terms of what steps do we need to understand to complete a task <include and example here>.

### Use standard or well-established packages (unless introducing a new package)
Aim to use packages either from the standard library or well-established packages.  Obscure packages or packages that are no longer
maintained may introduce too many dependencies or end up breaking code.  The only exception here is if we are introducing a new package.

### Use small data sets to reduce download time and make it quicker for a user to work through the tutorial

### Avoid writing helper functions in a separate module
Repying on helper functions stored in a separate module will hide what we are trying to teach and could also decrease the ability of users to recreate code.

The only exception here is if we are teaching writing code.
