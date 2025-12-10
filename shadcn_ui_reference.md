# shadcn/ui Reference Guide

## Philosophy
shadcn/ui is **NOT** a component library that you install as a dependency (like MUI or Chakra UI).
Instead, it is a collection of reusable components that you **copy and paste** into your apps.
- **Open Code**: You own the code. It lives in your project, not in `node_modules`.
- **Customizable**: Since the code is yours, you can modify it to fit your needs.
- **Styled with Tailwind CSS**: Built on top of Tailwind CSS and Radix UI.

## Project Structure
In this workspace (`chatbot-2311`), the configuration appears to be as follows:
- **Utils**: `src/lib/utils.ts` (Contains the `cn` helper for class merging).
- **Components**: typically located in `src/components/ui`.
- **Tailwind Config**: `tailwind.config.js`.

## Installation & Usage
To add components, use the CLI. Do not manually copy files unless necessary.

### CLI Command
```bash
npx shadcn@latest add <component-name>
```
Example:
```bash
npx shadcn@latest add button prompt accordion dialog
```

### Common Components
Here are some available components you can add:

- **Accordion**: Vertically stacked interactive headings.
- **Alert**: Displays a callout for user attention.
- **AlertDialog**: A modal dialog that interrupts the user with important content.
- **AspectRatio**: Displays content within a desired ratio.
- **Avatar**: An image element with a fallback for representing the user.
- **Badge**: Displays a badge or a component that looks like a badge.
- **Button**: Displays a button or a component that looks like a button.
- **Calendar**: A date field component that allows users to enter and edit date.
- **Card**: Displays a card with header, content, and footer.
- **Checkbox**: A control that allows the user to toggle between checked and not checked.
- **Collapsible**: An interactive component which expands/collapses a panel.
- **Command**: Fast, composable, unstyled command menu for React.
- **ContextMenu**: Displays a menu to the user when a right-click is triggered.
- **Dialog**: A window overlaid on either the primary window or another dialog window.
- **DropdownMenu**: Displays a menu to the user—such as a set of actions or functions—triggered by a button.
- **Form**: Building forms with React Hook Form and Zod.
- **HoverCard**: For sighted users to preview content available behind a link.
- **Input**: Displays a form input field or a component that looks like an input field.
- **Label**: Renders an accessible label associated with controls.
- **Menubar**: A visually persistent menu common in desktop applications.
- **NavigationMenu**: A collection of links for navigating websites.
- **Popover**: Displays rich content in a portal, triggered by a button.
- **Progress**: Displays an indicator showing the completion progress of a task.
- **RadioGroup**: A set of checkable buttons—known as radio buttons—where no more than one of the buttons can be checked at a time.
- **ScrollArea**: Augments native scroll functionality for custom, cross-browser styling.
- **Select**: Displays a list of options for the user to pick from—triggered by a button.
- **Separator**: Visually or semantically separates content.
- **Sheet**: Extends the Dialog component to display content that complements the main screen.
- **Skeleton**: Used to show a placeholder while content is loading.
- **Slider**: An input where the user selects a value from within a given range.
- **Switch**: A control that allows the user to toggle between checked and not checked.
- **Table**: A responsive table component.
- **Tabs**: A set of layered sections of content—known as tab panels—that are displayed one at a time.
- **Textarea**: Displays a form textarea or a component that looks like a textarea.
- **Toast**: A succinct message that is displayed temporarily.
- **Toggle**: A two-state button that can be either on or off.
- **Tooltip**: A popup that displays information related to an element when the element receives keyboard focus or the mouse hovers over it.

## Theming
Theming is handled via standard CSS variables in `globals.css` (or similar) and `tailwind.config.js`.
You can customize fonts, colors, and border radii in the `layer base` directives of your CSS file.

## AI Agent Instructions
When the "UI Integration Agent" or other agents need to use a UI component:
1.  **Check if it exists**: Look in `src/components/ui`.
2.  **Add if missing**: Suggest running `npx shadcn@latest add <component>`.
3.  **Usage**: Import from `@/components/ui/<component>`.
    ```tsx
    import { Button } from "@/components/ui/button"
    
    export function MyComponent() {
      return <Button variant="outline">Click me</Button>
    }
    ```
