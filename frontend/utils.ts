
export const formatBytes = (bytes: number, decimals = 2): string => {
    if (bytes === null || bytes === undefined || isNaN(bytes)) {
        return '';
    }
    if (bytes === 0) return '0 B';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

export const formatHandshake = (secondsElapsed: number): string => {
    if (!secondsElapsed || secondsElapsed === 0) {
        return 'Never';
    }

    // secondsElapsed is already the time difference in seconds
    if (secondsElapsed < 5) {
        return "Just now";
    }

    // Break down into hours, minutes, seconds
    const hours = Math.floor(secondsElapsed / 3600);
    const minutes = Math.floor((secondsElapsed % 3600) / 60);
    const seconds = Math.floor(secondsElapsed % 60);

    const parts: string[] = [];
    if (hours > 0) parts.push(`${hours} hour${hours > 1 ? 's' : ''}`);
    if (minutes > 0) parts.push(`${minutes} minute${minutes > 1 ? 's' : ''}`);
    if (seconds > 0 || parts.length === 0) parts.push(`${seconds} second${seconds > 1 ? 's' : ''}`);

    return parts.join(', ');
}
