export function canCancel(placedAtIso: string, eligibilityDays: number): boolean {
  const placed = new Date(placedAtIso);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - placed.getTime()) / (1000 * 60 * 60 * 24));
  return diffDays < eligibilityDays; // strictly less than N days
}