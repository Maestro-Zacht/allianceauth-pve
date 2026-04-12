import { useReducer, useEffect, type Reducer, type Dispatch } from 'react';



export function useLocalStorageReducer<S, A>(
    key: string | null,
    reducer: Reducer<S, A>,
    initialState: S
): [S, Dispatch<A>, () => void] {
    const init = (defaultState: S): S => {
        if (key === null)
            return defaultState;

        try {
            const item = window.localStorage.getItem(key);
            if (item)
                return JSON.parse(item);

            if (defaultState instanceof Function)
                return defaultState();

            return defaultState;
        } catch (error) {
            console.warn(`Error reading localStorage key "${key}": `, error);
            return defaultState;
        }
    };

    const [state, dispatch] = useReducer(reducer, initialState, init);

    useEffect(() => {
        if (key !== null) {
            try {
                window.localStorage.setItem(key, JSON.stringify(state));
            } catch (error) {
                console.warn(`Error setting localStorage key "${key}":`, error);
            }
        }
    }, [key, state]);

    const resetLocalStorage = () => {
        if (key !== null) {
            try {
                window.localStorage.removeItem(key);
            } catch (error) {
                console.warn(`Error removing localStorage key "${key}":`, error);
            }
        }
    };

    return [state, dispatch, resetLocalStorage];
}