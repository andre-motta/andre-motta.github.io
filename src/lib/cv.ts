/** Public CV schema produced by scripts/import-cv.py. */

export interface CvEntry {
  organization: string;
  location: string;
  role: string;
  period: string;
  bullets: string[];
}

export interface CvEducation {
  institution: string;
  degree: string;
  period: string;
  details: string[];
}

export interface CvSkillGroup {
  category: string;
  items: string[];
}

export interface CvDocument {
  schemaVersion: 1;
  summary: string;
  summaryHighlights?: string[];
  expertise: string[];
  experience: CvEntry[];
  education: CvEducation[];
  additionalExperience: CvEntry[];
  research: CvEntry[];
  skills: CvSkillGroup[];
}

export const cvJsonPath = '../../.generated/cv.json';
export const cvPdfPath = '/extra/Andre_Motta_Resume.pdf';

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string' && item.trim().length > 0);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

function hasOnlyKeys(value: Record<string, unknown>, keys: readonly string[]): boolean {
  const allowed = new Set(keys);
  return Object.keys(value).every((key) => allowed.has(key));
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isEntry(value: unknown): value is CvEntry {
  return (
    isRecord(value) &&
    hasOnlyKeys(value, ['organization', 'location', 'role', 'period', 'bullets']) &&
    isNonEmptyString(value.organization) &&
    typeof value.location === 'string' &&
    typeof value.role === 'string' &&
    isNonEmptyString(value.period) &&
    isStringArray(value.bullets)
  );
}

function isEducation(value: unknown): value is CvEducation {
  return (
    isRecord(value) &&
    hasOnlyKeys(value, ['institution', 'degree', 'period', 'details']) &&
    isNonEmptyString(value.institution) &&
    isNonEmptyString(value.degree) &&
    isNonEmptyString(value.period) &&
    isStringArray(value.details)
  );
}

function isSkillGroup(value: unknown): value is CvSkillGroup {
  return (
    isRecord(value) &&
    hasOnlyKeys(value, ['category', 'items']) &&
    isNonEmptyString(value.category) &&
    isStringArray(value.items)
  );
}

/** Validate JSON loaded from the generated adapter output before rendering it. */
export function assertCvDocument(value: unknown): CvDocument {
  if (!isRecord(value)) {
    throw new Error('Generated CV must be an object');
  }
  if (
    !hasOnlyKeys(value, [
      'schemaVersion',
      'summary',
      'summaryHighlights',
      'expertise',
      'experience',
      'education',
      'additionalExperience',
      'research',
      'skills',
    ]) ||
    value.schemaVersion !== 1 ||
    !isNonEmptyString(value.summary) ||
    !isStringArray(value.expertise) ||
    value.expertise.length === 0 ||
    !Array.isArray(value.experience) ||
    value.experience.length === 0 ||
    !value.experience.every(isEntry) ||
    !Array.isArray(value.education) ||
    value.education.length === 0 ||
    !value.education.every(isEducation) ||
    !Array.isArray(value.additionalExperience) ||
    value.additionalExperience.length === 0 ||
    !value.additionalExperience.every(isEntry) ||
    !Array.isArray(value.research) ||
    value.research.length === 0 ||
    !value.research.every(isEntry) ||
    !Array.isArray(value.skills) ||
    value.skills.length === 0 ||
    !value.skills.every(isSkillGroup) ||
    (value.summaryHighlights !== undefined && !isStringArray(value.summaryHighlights))
  ) {
    throw new Error('Generated CV does not match schema version 1');
  }
  return value as unknown as CvDocument;
}
