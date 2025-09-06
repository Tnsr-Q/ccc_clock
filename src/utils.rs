// Utility functions for the CCC Clock application

/// Format a duration in seconds as MM:SS format
pub fn format_time(seconds: f64) -> String {
    let minutes = (seconds / 60.0) as u32;
    let secs = (seconds % 60.0) as u32;
    format!("{:02}:{:02}", minutes, secs)
}

/// Format a duration in seconds with centiseconds as MM:SS.CC format
pub fn format_time_precise(seconds: f64) -> String {
    let minutes = (seconds / 60.0) as u32;
    let secs = (seconds % 60.0) as u32;
    let centiseconds = ((seconds % 1.0) * 100.0) as u32;
    format!("{:02}:{:02}.{:02}", minutes, secs, centiseconds)
}

/// Convert minutes and seconds to total seconds
pub fn to_seconds(minutes: u32, seconds: u32) -> f64 {
    (minutes * 60 + seconds) as f64
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_time() {
        assert_eq!(format_time(125.0), "02:05");
        assert_eq!(format_time(59.0), "00:59");
        assert_eq!(format_time(3661.0), "61:01");
    }

    #[test]
    fn test_format_time_precise() {
        assert_eq!(format_time_precise(125.37), "02:05.37");
        assert_eq!(format_time_precise(59.99), "00:59.99");
    }

    #[test]
    fn test_to_seconds() {
        assert_eq!(to_seconds(2, 5), 125.0);
        assert_eq!(to_seconds(0, 59), 59.0);
        assert_eq!(to_seconds(1, 1), 61.0);
    }
}