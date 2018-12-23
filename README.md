# StarCraft II AI

This is a fairly simple Protoss AI that uses [python-sc2](https://github.com/Dentosal/python-sc2) to manage micro and macro, and uses a CNN to decide basic combat decisions. It uses mass Voidrays so there is a chance to win versus a hard difficulty Zerg AI.

## Getting started

**Prerequisites**

You will need Python 3.6 and [python-sc2](https://github.com/Dentosal/python-sc2):
```
pip3 install --user --upgrade sc2
```

For more information visit the library's github.

You will also need [opencv](https://github.com/opencv/opencv), [numpy](https://github.com/numpy/numpy) and [keras](https://github.com/keras-team/keras).

```
pip3 install  -- upgrade opencv-contrib-python
pip3 install  --upgrade numpy
pip3 install --upgrade keras
```

I didn't use my own model so download the model from [here](https://drive.google.com/file/d/10lj3vo3nsEMhJayD-K-JFM8t-3BQYmWV/view) and add it to the cloned directory.


### Running

After installing all the prerequisites carefully, you're ready to get started. 

```
python3 run_game.py
```

If you want to simply use the AI in your own project just import it.

```python
from sc2_bot import SCIIBot
```


## Help and support
If you have any ideas, requests or problems please create a [new issue](https://github.com/l2cup/SC2Bot/issues/new). 

## Special Thanks
Special thanks to [sentdex](https://www.youtube.com/user/sentdex) for the SC2AI tutorial and the model, also thanks to [BurnySc2](https://github.com/Dentosal/python-sc2/commits/master/examples/terran/mass_reaper.py?author=BurnySc2) for the micro i modified.
