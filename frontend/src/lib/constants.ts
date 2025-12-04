// Resort to pass mapping - mirrors ref__resort_pass_mapping table
export const RESORT_PASS_MAPPING: Record<string, string> = {
  'arapahoebasin': 'ikon',
  'arapahoe basin': 'ikon',
  'breckenridge': 'epic',
  'copper': 'ikon',
  'copper mountain': 'ikon',
  'crested butte': 'epic',
  'crestedbutte': 'epic',
  'keystone': 'epic',
  'loveland': 'indy',
  'monarch': 'indy',
  'purgatory': 'indy',
  'steamboat': 'ikon',
  'telluride': 'epic',
  'vail': 'epic',
  'winterpark': 'ikon',
  'winter park': 'ikon',
};

export type PassType = 'ikon' | 'epic' | 'indy';

export const PASS_OPTIONS: { value: string; label: string }[] = [
  { value: 'all', label: 'All Passes' },
  { value: 'ikon', label: 'Ikon' },
  { value: 'epic', label: 'Epic' },
  { value: 'indy', label: 'Indy' },
];

// Helper function to get pass type for a resort
export const getResortPass = (resortName: string): string | null => {
  const normalized = resortName.toLowerCase().trim();
  return RESORT_PASS_MAPPING[normalized] || null;
};

