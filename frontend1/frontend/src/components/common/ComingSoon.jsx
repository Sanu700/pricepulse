import { Sparkles } from "lucide-react";

function ComingSoon({ label = "Coming Soon" }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-brand-200 bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-700 dark:border-brand-500/30 dark:bg-brand-500/10 dark:text-brand-300">
      <Sparkles size={11} />
      {label}
    </span>
  );
}

export default ComingSoon;
