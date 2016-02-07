
from __future__ import with_statement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SubjectSlot import subject_slot

class PlayheadComponent(ControlSurfaceComponent):
    """
    Updates the contents of the Live playhead object.
    """

    def __init__(self, paginator = None, grid_resolution = None, follower = None, notes = range(8), triplet_notes = range(6), *a, **k):
        super(PlayheadComponent, self).__init__(*a, **k)
        self._playhead = None
        self._clip = None
        self._paginator = paginator
        self._grid_resolution = grid_resolution
        self._follower = follower
        self._notes = tuple(notes)
        self._triplet_notes = tuple(triplet_notes)
        self._on_page_changed.subject = self._paginator
        self._on_grid_resolution_changed.subject = self._grid_resolution
        self._on_follower_is_following_changed.subject = self._follower

    def set_playhead(self, playhead):
        self._playhead = playhead
        self.update()

    def set_clip(self, clip):
        self._clip = clip
        self._on_playing_status_changed.subject = clip
        self._on_song_is_playing_changed.subject = self.song() if clip else None
        self.update()

    @subject_slot('page')
    def _on_page_changed(self):
        self.update()

    @subject_slot('playing_status')
    def _on_playing_status_changed(self):
        self.update()

    @subject_slot('is_playing')
    def _on_song_is_playing_changed(self):
        self.update()

    @subject_slot('index')
    def _on_grid_resolution_changed(self):
        self.update()

    @subject_slot('is_following')
    def _on_follower_is_following_changed(self, value):
        self.update()

    def update(self):
        super(PlayheadComponent, self).update()
        if self._playhead:
            if self.is_enabled() and self.song().is_playing and self._clip and self._clip.is_playing:
                clip_slot = self._clip.canonical_parent
                track = clip_slot.canonical_parent if clip_slot else None
            else:
                track = None
            self._playhead.track = track
            if track:
                is_triplet = self._grid_resolution.clip_grid[1]
                notes = self._triplet_notes if is_triplet else self._notes
                self._playhead.notes = list(notes)
                self._playhead.wrap_around = self._follower.is_following and self._paginator.can_change_page
                self._playhead.start_time = self._paginator.page_length * self._paginator.page_index
                self._playhead.step_length = self._paginator.page_length / len(notes)