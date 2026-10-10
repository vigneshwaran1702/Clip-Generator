/**
 * Converts seconds into HH:MM:SS or MM:SS format.
 *
 * Examples:
 * formatDuration(65) -> "01:05"
 * formatDuration(3661) -> "01:01:01"
 */

export function formatDuration(totalSeconds) {
  if (
    totalSeconds === null ||
    totalSeconds === undefined ||
    Number.isNaN(totalSeconds)
  ) {
    return "00:00";
  }

  const seconds = Math.max(0, Math.floor(totalSeconds));

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;

  const pad = (value) => String(value).padStart(2, "0");

  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(remainingSeconds)}`;
  }

  return `${pad(minutes)}:${pad(remainingSeconds)}`;
}

export default formatDuration;