**Pseudocode plan for implementing crashing visualizations (step-by-step network diagrams):**

1. **Collect step-by-step graphs:**  
    - After running crashing optimization, for each crash step, create a copy of the network graph with updated durations.
    - Store each step as a tuple: (step_number, activity_crashed, new_duration, graph_copy).
    - Store all steps in a list (e.g., `self.step_graphs`).

2. **Show the first step:**  
    - When the user opens the crashing tab or after optimization, display the first step's network diagram.
    - Use a drawing function (e.g., `_draw_network_diagram_on_ax`) to render the graph on a matplotlib axis in the GUI.

3. **Navigation controls:**  
    - Provide buttons or controls for "First", "Previous", "Next", "Last", and "Go to step".
    - When a navigation control is used, update the display to show the corresponding step's network diagram.

4. **Show all steps grid:**  
    - Optionally, provide a button to show all step diagrams in a grid in a new window.

5. **Ensure GUI updates:**  
    - After each navigation, clear the previous diagram and draw the new one.
    - Update step info labels and spinboxes accordingly.

**What is already present in your code:**
- The logic for collecting step-by-step graphs is in `show_crashing_steps_diagrams`.
- The drawing logic is in `_draw_network_diagram_on_ax` and `_draw_network_diagram_on_ax_small`.
- Navigation methods (`show_first_step`, `show_next_step`, etc.) are implemented.
- The GUI for navigation (buttons, spinbox) is present in `create_crashing_tab`.

**What you need to do:**
- Make sure `run_crashing_optimization` calls `show_crashing_steps_diagrams` after crashing.
- Ensure `show_step` is called after updating `self.current_step`.
- Ensure navigation controls are correctly wired to the navigation methods.
- Optionally, add a "Show All Steps" button if not present.

**Summary:**  
You mostly need to ensure the GUI calls `show_crashing_steps_diagrams` after crashing, and that navigation controls call the correct methods to update the diagram. The core logic and visualization functions are already implemented in your code.