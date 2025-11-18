"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type SeparatorProps = React.HTMLAttributes<HTMLDivElement> & {
  orientation?: "horizontal" | "vertical";
};

const orientationClasses: Record<string, string> = {
  horizontal: "h-px w-full",
  vertical: "h-full w-px",
};

const Separator = React.forwardRef<HTMLDivElement, SeparatorProps>(
  ({ className, orientation = "horizontal", role = "separator", ...props }, ref) => (
    <div
      ref={ref}
      role={role}
      className={cn(
        "bg-border",
        orientationClasses[orientation],
        orientation === "vertical" ? "mx-2" : "my-2",
        className
      )}
      {...props}
    />
  )
);
Separator.displayName = "Separator";

export { Separator };
