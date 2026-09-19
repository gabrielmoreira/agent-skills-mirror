## SC 2.5.7 - Dragging Movements (Level AA)

All functionality that uses a dragging movement for operation can be achieved by a single pointer without dragging, unless dragging is essential or the functionality is determined by the user agent.

## SC: 2.5.7 - Dragging Movements (Level AA)

Analyze the files using following context:

_Goal_: Don't rely on dragging for a user action. A simple pointer alternative should be provided for actions that involves dragging operation, unless dragging is essential or the functionality is determined by user agent. This requirement applies to web content that interprets pointer actions.

_What to do_: Review the provided code for single pointer mode of operation for every dragging movement, without needing to drag elements. Not all users are capable of dragging actions while others use some alternative input devices which makes the dragging actions difficult. The 2.5.7 SC requirement is separate from keyboard accessibility. Keyboard specific actions like tabbing or arrow keys may not be available when encountering a drag-and-drop control. Providing text input can be an acceptable single-pointer alternative to a dragging movement action.

- Following are some discrete actions that are performed to establish a dragging movement:
  - tap or click to establish start position, then ...
  - press and hold that contact while ...
  - reposition the pointer before ...
  - release the pointer at end position
- Achieving keyboard equivalence (SC 2.1.1 and SC 2.1.3) for any dragging operation does not automatically meets 2.5.7 SC requirement and each requirement must be assessed independently.
- 2.5.7 SC applies to dragging operations, as opposed to pointer gestures which is covered under a separate SC 2.5.1. Only start and end point of movement matters and not the path itself.

Alternative for dragging movement on the same page can be executed with an equivalent option that allows for single pointer access without needing drag operation. It does not have to be the same component as long as the functionality is same. One example of this would be a color picker wheel, where a color can be changed by dragging the indicator. In addition, there could be text fields that allow the user to input a numerical color value without needing a drag movement.

Some more examples of single pointer alternatives are:

- A map allows users to drag the map view, while also providing up/down/left/right controls to move the view.
- A list of elements, alongside the ability to drag, also provides controls to move an element up/down by simply clicking on controls.
- A taskboard that allows users to drag-and-drop between different columns, also provides a pop-menu to move selected element.
- Radial controls that allow users to drag the marker/pointer to a position, also allows to pick a value and set marker to it.
- Linear slider controls allow tapping or clicking on any point of the slider track to change and set the value.

_Rules to follow_:

- For interface elements that require or support a dragging operation:
  - Check the interface for the presence of functions triggered by dragging movement.
  - Check that there is a single pointer alternative activation that does not require dragging to operate the same function.
- For each component that violates rule #1 above, compile a concise list of issues that user can review.

- For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
