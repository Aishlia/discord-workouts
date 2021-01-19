import asyncio
import discord
import logging
import os

from interval_timer import IntervalTimer, TimerPhase

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

OUR_DIR = os.path.abspath(os.path.basename(__file__))
DEFAULT_SOUND_DIR = os.path.join(OUR_DIR, "sounds")

class VoiceAnnouncer:
    def __init__(self, voice_client: discord.VoiceClient, sound_dir=DEFAULT_SOUND_DIR):
        self._voice_client = voice_client
        self._sound_dir = sound_dir

    def on_timer_tick(self, phase, done, remaining, halfway_sound:bool = False):
        print(f'Phase {phase} with {done} seconds done and {remaining} seconds remaining.')

        # Countdown is delivered as one audio file to avoid stuttering due to rate limiting, routing etc.
        if remaining == 3:
            # Note that this seems to be non-blocking without wrapping it into a task or alike.
            self._play_sound('countdown.mp3')

        if remaining == 5 and (phase == TimerPhase.Rest or phase == TimerPhase.Preparation):
            self._play_sound('prepare.mp3')

        # Play sound halfway through the work phase if it is 30 seconds or longer.
        print(halfway_sound)
        if halfway_sound and done + remaining > 10:  # Check if it is long enough for halfway_sound to not interfere
        # with Countdown
            # We get ticks for every full second.
            # If work is set for an uneven amount of seconds, we cannot hit the exact half.
            # Play sound half a second earlier then.
            if done == remaining or done + 1 == remaining:
                self._play_sound('halfway_sound.mp3')

    def _play_sound(self, sound_file: str):
        sound_path = os.path.join(self._sound_dir, sound_file)
        self._voice_client.play(discord.FFmpegPCMAudio(sound_path))

    def on_timer_started(self):
        self._play_sound('timer-set.mp3')

    def on_timer_ended(self):
        self._play_sound('all-done.mp3')

    def attach(self, timer: IntervalTimer):
        # Attach to the timer events.
        timer.started += self.on_timer_started
        timer.tick += self.on_timer_tick
        timer.ended += self.on_timer_ended

    def detach(self, timer: IntervalTimer):
        timer.started -= self.on_timer_started
        timer.tick -= self.on_timer_tick
        timer.ended -= self.on_timer_ended
