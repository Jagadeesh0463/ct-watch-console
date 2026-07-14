import { Globe, ShieldAlert, AlertTriangle, ShieldCheck } from "lucide-react";

const TONE = {
  primary: { icon: Globe, ring: "text-primary", bg: "bg-primary-bg" },
  critical: { icon: ShieldAlert, ring: "text-critical", bg: "bg-critical-bg" },
  warning: { icon: AlertTriangle, ring: "text-warning", bg: "bg-warning-bg" },
  healthy: { icon: ShieldCheck, ring: "text-healthy", bg: "bg-healthy-bg" },
};

export default function StatCard({ label, value, tone }) {
  const { icon: Icon, ring, bg } = TONE[tone] ?? TONE.primary;
  return (
    <div className="group rounded-xl border border-border bg-surface p-4 shadow-card transition-colors hover:border-border-hover">
      <div className="flex items-center justify-between">
        <span className="text-[12px] font-medium text-muted">{label}</span>
        <span className={`flex h-7 w-7 items-center justify-center rounded-md ${bg}`}>
          <Icon className={`h-3.5 w-3.5 ${ring}`} strokeWidth={2.25} />
        </span>
      </div>
      <div className="mt-2 text-2xl font-semibold tracking-tight text-white">{value}</div>
    </div>
  );
}
