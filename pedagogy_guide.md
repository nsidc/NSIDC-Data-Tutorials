__This is a collection of thoughts on pedgogy for tutorials that draws on ideas from the Carpentries.  It also includes some ideas on
content from divio.com and EarthCube__

### Have a well defined purpose for your notebook
Each notebook should have a clear description of what is covered and what the learning outcomes are.

### Enumerate learning objectives


### Consider your audience
Are they beginners with no experience of writing code, or are they experienced coders who just want to find the best way to read some data 

### Consider the duration of the tutorial

### Consider the aim/objective of the note book
Is the notebook a Tutorial to teach a concept or tool or a How To Guide to show how to perform a task?  Is the notebook intended to be self guided or taught by an instructor in a workshop?
[divio.com](https://documentation.divio.com/structure/) provide a good overview of the differences between Tutorials and How-To Guides; both describe practical steps but Tutorials designed
to allow users to understand concepts, whereas How-To Guides are more problem orientated and designed to solve problems that come up during working.  


### Avoid cognitive overload by focusing on one main task to complete
__Not the only or best guide but useful__ https://blog.innerdrive.co.uk/4-ways-to-overcome-cognitive-overload?hs_amp=true
Notebooks should be for a single - short - task.  This avoids cognitive overload.

### Follow best practices for coding but avoid overly complicated code.
Code needs to be understandable rather than efficient
Avoiding trying to write code as a 'developer'
We should aim to follow best practices for coding but also avoid overly complicated code that obscures the teaching aim; there is no need to include code to manage errors and exceptions.  Tutorial code does not need to be efficient but instead understandable.  Including some "like-this not like-this" examples might be helpful here.


### Avoid long code blocks
If a code block is so long that users cut-and-paste the code or press shift-enter then they are not learning, just copying.  The Carpentries advocate live-coding, where an instructor types code in real-time, correcting mistakes as the go and describing what they are doing.  This approach helps with pacing and length of content.  While most useful in workshops, thinking of writing code live, even for self-guided tutorials, will help keep coding manageable and cognitive load manageable.

Short code blocks also help break tasks into understandable steps.  Think in terms of what steps do we need to understand to complete a task <include and example here>.

### Use standard or well-established packages (unless introducing a new package)
We should aim to use packages either from the standard library or well-established packages - unless we are introducing a new package.

### Use small data sets to reduce download time and make it quicker for a user to work through the tutorial


### Avoid writing helper functions in a separate module
in order to increase transparency with the user in terms of what we are trying to teach them
we are hiding what we are trying to teach - unless we are teaching writing functions.

