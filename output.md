# Built-in React Hooks

## State Hooks

- State lets a component ["remember" information like user input.](/learn/state-a-components-memory)

  - [useState](/reference/react/useState) declares a state variable that you can update directly.
  - [useReducer](/reference/react/useReducer) declares a state variable with the update logic inside a [reducer function.](/learn/extracting-state-logic-into-a-reducer)

```
markdown
    function ImageGallery() {
        const [index, setIndex] = useState(0);
        // ...
    }

    function ImageGallery() {
        const [index, setIndex] = useState(0);
        // ...
    }
```

## Context Hooks

- Context lets a component [receive information from distant parents without passing it as props.](/learn/passing-props-to-a-component)

  - [useContext](/reference/react/useContext) reads and subscribes to a context.

```
    function Button() {
        const theme = useContext(ThemeContext);
        // ...
    }

    function Button() {
        const theme = useContext(ThemeContext);
        // ...
    }
```

## Ref Hooks

- Refs let a component [hold some information that isn’t used for rendering,](/learn/referencing-values-with-refs) like a DOM node or a timeout ID.

  - [useRef](/reference/react/useRef) declares a ref.
  - [useImperativeHandle](/reference/react/useImperativeHandle) lets you customize the ref exposed by your component.

```
    function Form() {
        const inputRef = useRef(null);
        // ...
    }

    function Form() {
        const inputRef = useRef(null);
        // ...
    }
```

## Effect Hooks

- Effects let a component [connect to and synchronize with external systems.](/learn/synchronizing-with-effects)

  - [useEffect](/reference/react/useEffect) connects a component to an external system.

```
    function ChatRoom({ roomId }) {
        useEffect(() => {
            const connection = createConnection(roomId);
            connection.connect();
            return () => connection.disconnect();
        }, [roomId]);
        // ...
    }

    function ChatRoom({ roomId }) {
        useEffect(() => {
            const connection = createConnection(roomId);
            connection.connect();
            return () => connection.disconnect();
        }, [roomId]);
        // ...
    }
```

Effects are an “escape hatch” from the React paradigm. Don’t use Effects to orchestrate the data flow of your application. If you’re not interacting with an external system, [you might not need an Effect.](/learn/you-might-not-need-an-effect)

There are two rarely used variations of `useEffect` with differences in timing:

- [useLayoutEffect](/reference/react/useLayoutEffect) fires before the browser repaints the screen. You can measure layout here.
- [useInsertionEffect](/reference/react/useInsertionEffect) fires before React makes changes to the DOM. Libraries can insert dynamic CSS here.

## Performance Hooks

- A common way to optimize re-rendering performance is to skip unnecessary work.

  - [useMemo](/reference/react/useMemo) lets you cache the result of an expensive calculation.
  - [useCallback](/reference/react/useCallback) lets you cache a function definition before passing it down to an optimized component.

```
    function TodoList({ todos, tab, theme }) {
        const visibleTodos = useMemo(() => filterTodos(todos, tab), [todos, tab]);
        // ...
    }
```

Sometimes, you can’t skip re-rendering because the screen actually needs to update. In that case, you can improve performance by separating blocking updates that must be synchronous (like typing into an input) from non-blocking updates which don’t need to block the user interface (like updating a chart).

- [useTransition](/reference/react/useTransition) lets you mark a state transition as non-blocking and allow other updates to interrupt it.
- [useDeferredValue](/reference/react/useDeferredValue) lets you defer updating a non-critical part of the UI and let other parts update first.

## Other Hooks

- These Hooks are mostly useful to library authors and aren’t commonly used in the application code.

  - [useDebugValue](/reference/react/useDebugValue) lets you customize the label React DevTools displays for your custom Hook.
  - [useId](/reference/react/useId) lets a component associate a unique ID with itself. Typically used with accessibility APIs.
  - [useSyncExternalStore](/reference/react/useSyncExternalStore) lets a component subscribe to an external store.
  - [useActionState](/reference/react/useActionState) allows you to manage state of actions.

## Your own Hooks

- You can also [define your own custom Hooks](/learn/reusing-logic-with-custom-hooks#extracting-your-own-custom-hook-from-a-component) as JavaScript functions.
