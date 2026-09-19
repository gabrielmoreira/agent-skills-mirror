## SC 3.2.2 - On Input (Level A)

Changing the setting of any user interface component does not automatically cause a change of context unless the user has been advised of the behavior before using the component.

## SC: 3.2.2 - On Input (Level A)

Analyze the files using following context:

_Goal_: Content can be operated predictably, users (including users with disabilities) will need to be forewarned if a context change is expected based on their inputs.

_What to do_ : Review provided HTML and JS code for accessibility violations per WCAG 3.2.2 'On Input'. Ensure that content in the user interface component behaves predictably, including actions such as checking a checkbox, entering text, changing a selection on a dropdown. Changes in context can confuse users who do not perceive the change or are easily distracted by it. Clicking on links or buttons is considered as activating a control, and not changing the setting of that control.

Unexpected changes in context can be disorienting to users with disabilities, visual or cognitive limitations that they are unable to use the content. Individuals who cannot detect changes of context are less likely to become disoriented while navigating a site for example. Some people with low-vision, with reading and intellectual disabilities, and others who have difficulty interpreting visual cues may benefit from providing additional cues in order to detect such changes of context.

Some examples:

- A web-based calendaring form includes standard fields for subject, time, and location, along with radio buttons to select the entry type: meeting, appointment, or reminder etc. A user selecting "meeting" can add fields for participants, while selecting "reminder" displays different fields. The form's overall structure however remains consistent despite these changes.
- For phone numbers in US, the form can have separate fields for the area code, prefix and number. As the user completes one field, the focus automatically moves to the next field. This behavior is explained at the form's start.

Following are some sufficient techniques that WCAG working group deems sufficient to be used to meet this success criterion:

- G80: Providing a submit button to make it easier for users to initiate a change of context.
  - H32: Find all forms, and for each form check that it has a submit button.
  - H84: For each 'select' element/button combination, check that focus (including keyboard focus) on an option in the 'select' element does not result in any actions. Also check that selecting button performs action associated with current 'select' element.
- G13: Providing a description on what will happen before a change to a form control that causes a context change. Locate the content where change of the setting of a form control will result in a change of context, and check to see if there is an explanation or description of what will happen when the control is changed, is available prior to the control activations.
- SCR19: Using 'onchange' event on a select element without causing a change of context. This is achieved by following algorithm:
  1. Navigate to trigger select element and change the value of the select.
  2. Navigate to select element that is updated by trigger, check that matching option values are displayed in the other select element.
  3. Navigate to the trigger select element, navigate through the options but do not select or change the value. Check that the matching option values are still displayed in associated select element.

Note: A change of content is not always considered to be a change of context.

Note: G201, while beneficial for user experience, is considered an advisory technique for this success criterion and not sufficient on its own. G201 technique is as follows:

- For each link that opens automatically in a new window or tab, use the following algorithm:
  1. check if there is a warning spoken in assistive technology that this link opens to a new window
  2. check that there is a visual warning in text that this link opens to a new window

_Rules to follow_ :

- Require that content can be operated predictably. Users must be forewarned if a change of context is expected based on their inputs, per this WCAG 3.2.2 'On Input' success criterion.
- For each component that violates #1, compile a concise list of issues for user to review, along with an action report on sufficient technique that can help resolve violation for component under review.

- For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
- Opening a link or button target in a new browser tab or window (`target="_blank"` or a click handler that calls `window.open(...)`) is not an SC 3.2.2 violation. This criterion concerns unexpected context changes caused by changing a form control's value or state, not the expected result of deliberately activating a link or button. Treat indicating new-tab behavior as optional advisory guidance, never as a Level A or AA failure.
