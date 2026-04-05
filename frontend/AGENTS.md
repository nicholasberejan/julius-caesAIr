<!-- BEGIN:nextjs-agent-rules -->
# Front End Guidelines
- Whenever possible break components into smaller sub-components.
- Opt for generic components that can be reused across the app with styles applied dynamically.
- Look for opportunities to use factory patterns for components that share many characteristics but differ in layout or content.
- Avoid excessive logic in component code. Wherever possible, extract to utility or helper functions.
- Add jest tests for new components or changes to core logic.
- Avoid inline styling; use tailwind or other CSS classes.
- Strict typing. Do not use "any" type unless absolutely necessary.
<!-- END:nextjs-agent-rules -->
