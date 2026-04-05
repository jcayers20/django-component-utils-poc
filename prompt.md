I would like to create a set of utilties for creating common HTML components using Python data structures. I want to start with a basic one: the alert. You'll notice that I've created an empty file, alert.py, that we'll use to store the Python source code and a template file, alert.html (we can create more if required) to store the HTML snippet to render the alert.

Before we work through implementation, I want to work together to decide what features we would like to implement and what the API should look like. I can provide a start, but please don't consider this the final word; if there are other features that you think would be useful or if you disagree with my thoughts on API design please let me know. Do bear in mind that I want to have a consistent API design across all components so that it's easy for users to pick up.

I propose that the user be able to control the following:
* Alert type (e.g., info, warning, error, etc.)
* Icon to be displayed at left-hand side of alert
* Title
* Body
* Footer
* Whether the alert is dismissible

Please generate a high-level plan for how we can create an easy-to-use API allowing
users to create alerts with the features above (and any others you think I may
have missed).