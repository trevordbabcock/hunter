# Hunter
## Summary
This is a simple project to explore the idea of simulating a hunter trying to survive in his/her environment, and the development of all the systems necessary to accomplish that.

Currently, the gameplay is represented by ASCII characters rendered in a small console window. There is an H, the Hunter, that moves around and attempts to survive. The Hunter's vital stats are displayed on the left and the Hunter's action log is displayed at the bottom. When hungry, the Hunter will search for berries to eat or rabbits to hunt (the R's), and when tired, the Hunter will return to camp (C) to sleep.

There are two player controls right now:
- **F** - toggle fog of war
- **H** - toggle user interface

And that's it! This is not a game for playing so much as observing (like an ant farm). From this humble start, I hope to build a rich world that is genuinely enjoyable to observe. And eventually I do plan to add more ways for the player to interact with the world. But for now, you'll have to use your imagination. :)

If you really want to tinker, you can modify the stats in [this file](https://github.com/trevordbabcock/hunter/blob/master/hunter_pkg/config/stats.json). For example, in the "rabbit" section try changing "spawn" to 0.2 and see what happens. User beware: there are tons of ways to break the game messing with this file! 

<br/>
<img src="blog/img/dead-rabbit.png" alt="drawing" width="800"/>
<br/><br/>

For more info, see blog entries in the [blog directory](https://github.com/trevordbabcock/hunter.git). There, you can read about my progress, process, goals for the future, and general ruminations. [This post](https://github.com/trevordbabcock/hunter/blob/master/blog/2020.09.26.CREATURES.ECOSYSTEMS.md), where I organized my thoughts on how to simulate creatures of varying complexity, may be a particularly interesting starting point.

## Installation
### Using Python Eggs
Install pyenv. For MacOSX, run the following:
```
> brew install pyenv
```
Note: some other setup steps may be necessary.


Using pyenv, install Python 3.8 or higher:
```
> pyenv install 3.8.0
```

Install the Hunter egg:
```
> pip install hunter-tdb==0.8.0
```

Run the game!
```
> run hunter
```

### Running from source
Install python 3.8 or higher:
```
However you like. :)
```

Clone source:
```
git clone https://github.com/trevordbabcock/hunter.git
```

Install requirements:
```
cd hunter
pip install -r requirements.txt
```

Install Ruby 2.7.0 or higher (temporary step; will remove this requirement this soon).

Run the game:
```
./hunter_pkg/main.py
```

Have fun! Any feedback is welcome. :)