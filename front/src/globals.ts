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
    Formats allowed as conversion targets. ogg (VORBIS) and M4A (AAC)
*/
export const ALLOWED_FORMATS = ['ogg', 'm4a'];