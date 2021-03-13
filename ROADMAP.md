# Hunter
## Roadmap
* **v0 - prototype hunter surviving in basic environment/ecosystem**
  * ~~**v0.1** - remove tutorial code, add color, allow larger map, collision~~
  * ~~**v0.2** - add realtime game loop, add rabbits, add event queue~~
  * ~~**v0.3** - add berry bushes, add hunter eating berries, improve rabbit behavior~~
  * ~~**v0.4** - add first ui elements, add hunter hunger system and death, fix tech debt~~
  * ~~**v0.5** - add day/night cycle, add hunter action log, add fog of war, add tile examination~~
  * ~~**v0.6** - add hunter sleep, add hunter camp, track hunter stats, fog of war toggle,add hunter bow and arrow, add rabbit hunting~~
  * ~~**v0.7** - revise hunger/health/energy system, improve rabbit behavior, improve hunter ai~~
  * ~~**v0.8** - include procedural map generation, increase map size, improve game balance~~
  * ~~**v1.0** - add wolves, hunter vs wolf combat~~
* **v1 - playability, ui, and technical improvements**
  - add escape menu
    - pauses game
    - option to exit game
    - (eventual) option to save game
    - option to view controls
  - add ability to save and load game
  - make entities selectable
    - show stats for selected unit
    - make entities selectable and display action log just for that entity
    - allow selection while paused
    - when clicking on a cell with multiple entities, each click should select the next entity on that cell
    - the selected entity should be bolded in the cell entity list
  - change action system so that different actions can have different cooldowns
  - make creatures hideable
    - check boxes to show/hide
    - also show total number of each entity
  - fix hunter find-and-search-eat-berry duplication bug
    - add ellipses for duplicate messages
  - make hunter highlightable?
* **v2 - improve ecosystem**
  * **v2.1** - add another creature 1
  * **v2.2** - add another creature 2
  * **v2.3** - add point of interest 1
  * **v2.4** - add point of interest 2
* **v3 - prototype map size scaling**
  * **v3.1** - add ability to pan camera
* **v4 - improve graphics?**