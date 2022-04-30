/*
Copyright (C) 2022  Aurora McGinnis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation using version 3 of the License ONLY.

See LICENSE.txt for more information.

globals.ts - Contains configuration constants for the Web UI. Changing this requires
recompiling the front end.
*/

/*
    Value by which the pitch is to be scaled by the backend during conversion. 

    Set by default and is user-overridable
*/
export const DEFAULT_PITCH_SCALER = 1.25;

/*
    Value by which the tempo is to be scaled by the backend during conversion.

    Set by default and is user-overridable
*/
export const DEFAULT_TEMPO_SCALER = 1.10;

/*
    Maximum file size that the UI should accept. 

    Ideally, this reflects the backend's limits.
*/
export const MAX_FILE_SIZE = 20 * (1024 ** 2);

/*
    Formats allowed as conversion targets. ogg (VORBIS) and M4A (AAC).

    If you change this, the backend must also be modified to support the changes.
*/
export const ALLOWED_FORMATS = ['ogg', 'm4a'];

/*
    Buttons to display in the UI
*/
export const BUTTONS = [
    {'src': '/assets/github.svg', 'recolor': true, 'target': 'https://github.com/aurowora/nightconv', 'alt': 'GitHub'}
]