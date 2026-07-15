import { AlertTriangle } from "lucide-react";

function ErrorState({
  title = "Something went wrong",
  description = "That request failed. Try again in a moment.",
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-danger-soft bg-danger-soft/40 px-6 py-14 text-center">
      <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-danger-soft text-danger">
        <AlertTriangle size={22} />
      </span>
      <h3 className="text-lg font-semibold text-ink">{title}</h3>
      <p className="mt-1.5 max-w-sm text-sm text-muted">{description}</p>
    </div>
  );
}

export default ErrorState;
