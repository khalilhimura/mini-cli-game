import curses
import time
from colony import Colony
from game import generate_resources, build_structure, save_game, load_game, trigger_random_event, AVAILABLE_EVENT_CLASSES, resolve_major_event, BUILDING_CLASSES
from buildings import Mine, SolarPanel, HydroponicsFarm, ResearchLab # Import new buildings
import os

def draw_major_event_popup(stdscr, event_instance):
    """Draws a popup window for a major event with choices."""
    if not event_instance:
        return

    rows, cols = stdscr.getmaxyx()
    popup_height = 10 
    popup_width = cols - 20 
    if popup_width < 50 : popup_width = 50 
    if popup_height > rows -4 : popup_height = rows - 4

    popup_y = (rows - popup_height) // 2
    popup_x = (cols - popup_width) // 2

    popup = curses.newwin(popup_height, popup_width, popup_y, popup_x)
    popup.border()
    popup.bkgd(' ', curses.color_pair(1)) 

    popup.addstr(1, 2, event_instance.name, curses.A_BOLD | curses.color_pair(1))
    
    desc_lines = []
    current_line = ""
    max_line_width = popup_width - 4 
    for word in event_instance.description.split():
        if len(current_line) + len(word) + 1 > max_line_width:
            desc_lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += " "
            current_line += word
    if current_line:
        desc_lines.append(current_line)

    for i, line in enumerate(desc_lines):
        if i < 2 : 
             popup.addstr(3 + i, 2, line, curses.color_pair(1))

    choice_start_y = 3 + min(2, len(desc_lines)) + 1

    for i, choice in enumerate(event_instance.choices):
        choice_text = f"{i+1}. {choice['text']}"
        if len(choice_text) > max_line_width:
            choice_text = choice_text[:max_line_width-3] + "..."
        popup.addstr(choice_start_y + i, 2, choice_text, curses.color_pair(1))
        if i >= 1: 
            break 
    popup.refresh()
    return popup

def draw_build_menu(stdscr, colony_instance):
    """Draws the build menu."""
    rows, cols = stdscr.getmaxyx()
    menu_height = 10 + len(BUILDING_CLASSES) # Dynamic height
    menu_width = cols - 10 # Wider
    if menu_width < 60: menu_width = 60
    if menu_height > rows - 2 : menu_height = rows - 2

    menu_y = (rows - menu_height) // 2
    menu_x = (cols - menu_width) // 2

    build_win = curses.newwin(menu_height, menu_width, menu_y, menu_x)
    build_win.border()
    build_win.bkgd(' ', curses.color_pair(1)) # Using same color pair as major event for now

    build_win.addstr(1, 2, "BUILD MENU (Press 'q' to close)", curses.A_BOLD | curses.color_pair(1))
    
    buildable_items = list(BUILDING_CLASSES.items()) # Get items to access name and class

    for idx, (name, building_class) in enumerate(buildable_items):
        if idx >= menu_height - 4: # Ensure it fits in the window
            break
        
        # Create a temporary instance to get its cost
        temp_building = building_class()
        cost = temp_building.cost
        
        cost_parts = []
        for resource, amount in cost.items():
            # Assuming resource keys are like "Minerals", "Energy"
            # Take first letter for abbreviation, e.g., "M", "E"
            abbreviation = resource[0]
            cost_parts.append(f"{int(amount)}{abbreviation}")
        cost_string = ", ".join(cost_parts)
        
        # Check if player can afford it
        can_afford = colony_instance.has_enough_resources(cost)
        display_color = curses.color_pair(2) if can_afford else curses.color_pair(3) # Green if can afford, Red if not
        if not curses.has_colors(): display_color = curses.color_pair(1) # Fallback for no colors

        menu_item_text = f"{idx+1}. {name} (Cost: {cost_string})"
        if len(menu_item_text) > menu_width -4:
            menu_item_text = menu_item_text[:menu_width-7] + "..."

        build_win.addstr(3 + idx, 2, menu_item_text, display_color)

    build_win.refresh()
    return build_win


def main_curses(stdscr):
    # Initialize curses settings
    curses.curs_set(0)  
    stdscr.nodelay(True) 
    stdscr.timeout(1000) 

    # Initialize colors
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) 
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) 
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)   
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK) # For ResearchPoints
        stdscr.bkgd(' ', curses.color_pair(2)) 
    else: # Define a fallback for color_pair(4) if no colors
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)


    # Initialize Colony (using updated initial resources from colony.py)
    my_colony = Colony() 

    # Time and Event management
    last_update_time = time.time()
    event_trigger_interval = 10.0  
    time_since_last_event_check = 0.0

    # Game State
    current_game_state = "running" 
    active_major_event = None
    active_popup_window = None # Renamed for clarity (used for both major event and build menu)

    # Main game loop
    while True:
        current_time = time.time()
        time_delta = current_time - last_update_time
        last_update_time = current_time
        
        generate_resources(my_colony, time_delta)

        key = stdscr.getch()

        if key == ord('q') and current_game_state == "running": 
            break
        
        # State-specific input handling first
        if current_game_state == "major_event_popup":
            if active_major_event and active_popup_window: # Check if popup is active
                if key != -1:
                    chosen_option_idx = -1
                    if key == ord('1'): chosen_option_idx = 0
                    elif key == ord('2') and len(active_major_event.choices) > 1: chosen_option_idx = 1
                    
                    if chosen_option_idx != -1 and chosen_option_idx < len(active_major_event.choices):
                        choice_key_from_event = active_major_event.choices[chosen_option_idx]['key']
                        resolve_major_event(my_colony, active_major_event, choice_key_from_event)
                        
                        current_game_state = "running"
                        active_major_event = None
                        active_popup_window.clear()
                        active_popup_window = None
                        stdscr.clear() # Force redraw of main screen
                        stdscr.refresh()
            else: # Fallback if popup isn't active but state is set
                current_game_state = "running"

        elif current_game_state == "build_menu":
            if active_popup_window: # Check if build menu is active
                if key == ord('q') or key == curses.KEY_BACKSPACE: # Added KEY_BACKSPACE
                    current_game_state = "running"
                    active_popup_window.clear()
                    active_popup_window = None
                    stdscr.clear() # Force redraw
                    stdscr.refresh()
                elif ord('1') <= key <= ord(str(len(BUILDING_CLASSES))): # Check for numeric choice
                    buildable_types_list = list(BUILDING_CLASSES.values())
                    selected_idx = int(chr(key)) - 1
                    
                    if 0 <= selected_idx < len(buildable_types_list):
                        selected_building_class = buildable_types_list[selected_idx]
                        # build_structure already prints messages; we'll log to history too
                        # It returns True/False which is not the message.
                        # We need to craft a message or modify build_structure.
                        # For now, let's assume build_structure prints to console, and we log a generic one.
                        
                        # Get building name for the message
                        building_name_to_build = list(BUILDING_CLASSES.keys())[selected_idx]

                        # Check affordability before attempting to build
                        temp_b = selected_building_class()
                        if my_colony.has_enough_resources(temp_b.cost):
                            build_success = build_structure(my_colony, selected_building_class)
                            if build_success:
                                my_colony.add_event_to_history(f"Construction started: {building_name_to_build}.")
                            else: # Should not happen if has_enough_resources was true, but as a fallback
                                my_colony.add_event_to_history(f"Failed to start construction: {building_name_to_build} (unexpected error).")
                        else:
                            my_colony.add_event_to_history(f"Not enough resources to build {building_name_to_build}.")

                        current_game_state = "running" # Return to running after attempting to build
                        active_popup_window.clear()
                        active_popup_window = None
                        stdscr.clear() # Force redraw
                        stdscr.refresh()
            else: # Fallback
                current_game_state = "running"

        # "running" state input handling & logic (if not handled by popups)
        if current_game_state == "running":
            if key == ord('b'):
                current_game_state = "build_menu"
                # No need to clear active_popup_window here if it's None
            else: # Only trigger background events if not opening build menu
                time_since_last_event_check += time_delta
                if time_since_last_event_check >= event_trigger_interval:
                    potentially_major_event = trigger_random_event(my_colony, AVAILABLE_EVENT_CLASSES)
                    if potentially_major_event and potentially_major_event.is_major:
                        active_major_event = potentially_major_event
                        current_game_state = "major_event_popup"
                        my_colony.add_event_to_history(f"ALERT: {active_major_event.name[:30]}...")
                        # active_popup_window will be drawn in the display section
                    time_since_last_event_check = 0.0

        # Screen Drawing Logic (based on state)
        if current_game_state == "running":
            if active_popup_window: # Clear any previous popups if we are back to running state
                active_popup_window.clear()
                active_popup_window = None
            
            stdscr.clear()
            stdscr.addstr(0, 0, "Space Colony Idle - Real Time", curses.color_pair(2))
            stdscr.addstr(2, 0, "RESOURCES:", curses.color_pair(2))
            resources = my_colony.get_resources()
            stdscr.addstr(3, 2, f"Minerals: {resources.get('Minerals', 0.0):.1f}", curses.color_pair(2))
            stdscr.addstr(4, 2, f"Energy:   {resources.get('Energy', 0.0):.1f}", curses.color_pair(2))
            stdscr.addstr(5, 2, f"Food:     {resources.get('Food', 0.0):.1f}", curses.color_pair(2))
            stdscr.addstr(6, 2, f"Research: {resources.get('ResearchPoints', 0.0):.1f}", curses.color_pair(4)) # Yellow for RP


            building_y_start = 8
            stdscr.addstr(building_y_start, 0, "BUILDINGS:", curses.color_pair(2))
            buildings = my_colony.get_buildings()
            current_y_offset = building_y_start + 1
            if not buildings:
                stdscr.addstr(current_y_offset, 2, "None", curses.color_pair(2))
                current_y_offset += 1
            else:
                for i, building in enumerate(buildings):
                    stdscr.addstr(current_y_offset + i, 2, building.name, curses.color_pair(2))
                current_y_offset += len(buildings)

            event_history_y_start = current_y_offset + 1
            stdscr.addstr(event_history_y_start, 0, "EVENT HISTORY:", curses.color_pair(2))
            screen_height, screen_width = stdscr.getmaxyx()
            max_events_to_show = screen_height - (event_history_y_start + 1) - 3 # Reserve space for commands
            for i, event_msg in enumerate(my_colony.event_history[:max_events_to_show]):
                display_msg = event_msg[:screen_width - 4] 
                msg_color = curses.color_pair(2) # Default
                if "Lost" in event_msg or "failed" in event_msg or "Not enough" in event_msg:
                    msg_color = curses.color_pair(3) # Red
                elif "ALERT" in event_msg:
                    msg_color = curses.color_pair(4) # Yellow
                stdscr.addstr(event_history_y_start + 1 + i, 2, display_msg, msg_color)

            commands_y_start = screen_height - 2 
            stdscr.addstr(commands_y_start, 0, "COMMANDS:", curses.color_pair(2))
            stdscr.addstr(commands_y_start + 1, 2, "b: Build Menu, q: Quit", curses.color_pair(2))
            
            stdscr.refresh()

        elif current_game_state == "major_event_popup" and active_major_event:
            if not active_popup_window: # If popup wasn't created yet or was cleared
                 active_popup_window = draw_major_event_popup(stdscr, active_major_event)
            active_popup_window.refresh() # Keep popup visible

        elif current_game_state == "build_menu":
            if not active_popup_window: # If popup wasn't created yet or was cleared
                active_popup_window = draw_build_menu(stdscr, my_colony)
            active_popup_window.refresh() # Keep popup visible


if __name__ == "__main__":
    curses.wrapper(main_curses)
