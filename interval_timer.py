import asyncio
import enum

from event import Event

class IntervalTimer:
    def __init__(self):
        # Set up the events that any announcement services can listen to.
        self.started = Event()
        self.tick = Event()
        self.ended = Event()

        self._exercises = 9
        self._sets = 2
        self._workout_time = 30
        self._workout_rest = 10
        self._set_rest = 20

        self._task = None

    def running(self):
        return not (self._task is None or self._task.done())

    def print_config(self):
        # TODO: Make the next line shorter
        return f'{self._sets} sets of {self._exercises} exercises with '
        '{self._set_rest} seconds rest in between. {self._workout_time} '
        'seconds workout, {self._workout_rest} seconds rest'

    def start(self, exercises: int, sets: int, workout_time: int, workout_rest: int, set_rest: int):
        self._exercises = exercises
        self._sets = sets
        self._workout_time = workout_time
        self._workout_rest = workout_rest
        self._set_rest = set_rest

        self._task = asyncio.create_task(self._run_timer())
        self.started.invoke()
        print('Timer started.')

    def restart(self):
        self._task = asyncio.create_task(self._run_timer())
        self.started.invoke()
        print('Timer started.')

    def stop(self):
        self._task.cancel()
        print('Timer stopped.')

    async def _run_timer(self):
        # Start with a prep phase
        prep = 17
        prep_done = 0
        while prep_done < prep:
            await asyncio.sleep(1)
            prep_done += 1
            self.tick.invoke(phase=TimerPhase.Preparation, done=prep_done, remaining=prep - prep_done)

        # Note that the limits are exclusive upper bounds since we count starting from 0.
        exercises_done = 0
        sets_done = 0
        print(f'set {self._exercises} {self._sets} {self._workout_time} {self._workout_rest} {self._set_rest}')  # DEBUG
        while sets_done < self._sets:
            print(f'set {sets_done} starting')  #DEBUG
            while exercises_done < self._exercises:
                print(f'set {exercises_done} starting')  # DEBUG

                # Work phase.
                exercise_time = 0
                while exercise_time < self._workout_time:
                    print(exercise_time)
                    await asyncio.sleep(1)
                    exercise_time += 1
                    self.tick.invoke(phase=TimerPhase.Work, done=exercise_time, remaining=self._workout_time - exercise_time)

                exercises_done += 1
                # No need to do the rest phase after the last interval.
                if exercises_done == self._exercises:
                    print("break")
                    break

                # Exercise rest phase.
                exercise_rest_time = 0
                while exercise_rest_time < self._workout_rest:
                    await asyncio.sleep(1)
                    exercise_rest_time += 1
                    self.tick.invoke(phase=TimerPhase.Rest, done=exercise_rest_time, remaining=self._workout_rest - exercise_rest_time)


            if sets_done == self._sets:
                break

            # Set rest phase
            set_rest_done = 0
            while set_rest_done < self._set_rest:
                await asyncio.sleep(1)
                set_rest_done += 1
                self.tick.invoke(phase=TimerPhase.Rest, done=set_rest_done, remaining=self._set_rest - set_rest_done)

        # Wait to not clash with the last tick event.
        await asyncio.sleep(1)
        self.ended.invoke()
        print('Last interval completed.')



class TimerPhase(enum.Enum):
    Preparation = 1
    Work = 2
    Rest = 3
