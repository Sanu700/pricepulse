import { AlertTriangle } from "lucide-react";

function ErrorState({ title = "Something went wrong", description = "That request failed. Try again in a moment." }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-rose-200 bg-rose-50 px-6 py-14 text-center dark:border-rose-900/50 dark:bg-rose-950/30">
      <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-100 text-rose-600 dark:bg-rose-900/50 dark:text-rose-400">
        <AlertTriangle size={22} />
      </span>
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">{title}</h3>
      <p className="mt-1.5 max-w-sm text-sm text-zinc-500 dark:text-zinc-400">{description}</p>
    </div>
  );
}

export default ErrorState;
