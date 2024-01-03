import Utilities from './utilities';

describe('Utilities.throttle', () => {
    it('calls its callback after wait time', () => {
        jest.useFakeTimers();

        const callback = jest.fn();
        const throttled = Utilities.throttle(callback, 1000);

        throttled();

        expect(callback).not.toHaveBeenCalled();

        const dateNow = Date.now;
        Date.now = jest.fn().mockImplementationOnce(() => dateNow() + 1001);

        throttled();

        expect(callback).toHaveBeenCalled();
    });
});
