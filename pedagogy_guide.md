# Pedagogy Best Practices
Pedagogy is commonly understood as an approach to teaching.  The "Best Practices" listed below are meant as a guide
to developing Jupyter Notebooks for tutorials.  These tutorials may be self-guided tutorials intended for users to work through
on their own; or tutorials taught by an instructor in a workshop or hackathon environment.

The "Best Practices" draw on ideas from the [Carpentries](https://software-carpentry.org/) and also include some ideas on
content from [divio.com](divio.com) and [EarthCube notebooks](https://www.earthcube.org/notebooks).

### Have a well defined purpose for your notebook
What is the purpose of the tutorial?  Each notebook should have a clear description of what it covers.  Focusing on one task
is better than trying to cover multiple tasks.  See also [Avoid Cognitive Overload](#avoid-cognitive-overload).

Describe the purpose or aim of the notebook as an introduction.  If the aim is to produce a plot, include a PNG of the plot to show
the end result.

### Enumerate learning objectives
List the learning objectives after the notebook description.

### Consider your audience
Are they beginners with no experience of writing code, or are they experienced coders who just want to find the best way to read some data. 

### Consider the duration of the tutorial
Try to keep the time required to complete a notebook short.  This speaks to focusing on one task.  Users may give-up or loose interest if notebooks require too much time.
Thirty minutes is a good duration to aim for.

### Consider the aim/objective of the note book
Is the notebook a Tutorial to teach a concept or tool or a How To Guide to show how to perform a task?  Is the notebook intended to be self guided or taught by an instructor in a workshop?

[divio.com](https://documentation.divio.com/structure/) provide a good overview of the differences between Tutorials and How-To Guides; both describe practical steps but Tutorials are designed to help users to understand concepts, whereas How-To Guides are more problem orientated and designed to solve problems that come up during working.  

### Avoid Cognitive Overload 
Avoid cognitive overload by focusing notebook content on one main task.  Break complex notebooks into several notebooks.
Not the only or best guide but useful. https://blog.innerdrive.co.uk/4-ways-to-overcome-cognitive-overload?hs_amp=true
Notebooks should be for a single - short - task.  This avoids cognitive overload.

### Follow best practices for coding but avoid overly complicated code.
Aim to follow best practices for coding but also avoid overly complicated code that obscures the teaching aim.  For example, there is no need to
include code to manage errors and exceptions.

Code needs to be understandable rather than efficient.  Avoiding trying to write code as a 'developer'.

### Avoid long code blocks
If a code block is so long that users cut-and-paste the code or press shift-enter then they are not learning, just copying.  The Carpentries advocate live-coding,
where an instructor types code in real-time, correcting mistakes as they go and describing what they are doing.  This approach helps with pacing and length of content.

While most useful in workshops, thinking of writing code live, even for self-guided tutorials, will help keep coding manageable and the cognitive load manageable.

Short code blocks also help break tasks into understandable steps.  Think in terms of what steps do we need to understand to complete a task.

### Use standard or well-established packages (unless introducing a new package)
Aim to use packages either from the standard library or well-established packages.  Obscure packages or packages that are no longer
maintained may introduce too many dependencies or end up breaking code.  The only exception here is if we are introducing a new package.

### Use Live Coding for In-Person Tutorials
Live coding is where an instructor types code in real-time, talking through what they are doing, instead of cutting-and-pasting or just running code blocks.  Participants follow along also typing code.  This approach has advantages for pacing.  An instructor can only go as quickly as they can type.  Students get practice typing code.  Students also get to see mistakes, error messages, and solutions.
  
See this [article](https://carpentries.github.io/instructor-training/17-live/) from the Carpentries for more on live coding. 
  
### Use small data sets to reduce download time and make it quicker for a user to work through the tutorial
Users want to focus on learning how to perform tasks and not spend a lot of time downloading data.  Select sample datasets and files that take a __maximum of 3 minutes__ to download. In some caes, you may have to create files and datasets that are subsets of NSIDC hosted data. 
  
Download times may vary depending on the environment and platform where tutorials are being executed.  Tutorials designed for use in a cloud instance may be able to use larger datasets. 

### Avoid writing helper functions in a separate module
Relying on helper functions stored in a separate module will hide what we are trying to teach and could also decrease the ability of users to recreate code.

The only exception here is if we are teaching writing code.

## Resources
[Carpentries instructor training](https://carpentries.github.io/instructor-training/)  
[divio.com documentation guide](divio.com)  
[EarthCube peer-reviewed notebook examples](https://www.earthcube.org/notebooks)  
