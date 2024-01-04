// Common utility functions

class Utilities {
    // throttle function
    // example usage with a function called 'callback'
    // window.addEventListener('scroll', throttle(callback, 1000));
    static throttle(fn: () => void, wait: number) {
        let time = Date.now();
        return () => {
            if (time + wait - Date.now() < 0) {
                fn();
                time = Date.now();
            }
        };
    }
}

export default Utilities;
