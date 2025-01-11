type CaseTransformer = {
  toCamelCase: (str: string) => string;
  toSnakeCase: (str: string) => string;
  transformKeys: <T extends object>(obj: T, transformer: (key: string) => string) => any;
};

const caseTransformer: CaseTransformer = {
  toCamelCase: (str: string) => {
    return str.replace(/([-_][a-z])/g, (group) =>
      group.toUpperCase().replace('-', '').replace('_', '')
    );
  },

  toSnakeCase: (str: string) => {
    return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`).replace(/^_/, '');
  },

  transformKeys: <T extends object>(obj: T, transformer: (key: string) => string): any => {
    if (Array.isArray(obj)) {
      return obj.map(item => caseTransformer.transformKeys(item, transformer));
    }

    if (obj !== null && typeof obj === 'object') {
      return Object.keys(obj).reduce((acc, key) => {
        const value = obj[key as keyof T];
        const transformedKey = transformer(key);
        acc[transformedKey] = value !== null && typeof value === 'object'
          ? caseTransformer.transformKeys(value, transformer)
          : value;
        return acc;
      }, {} as Record<string, any>);
    }

    return obj;
  }
};

export const transformResponseToCamelCase = <T extends object>(data: T): any => {
  return caseTransformer.transformKeys(data, caseTransformer.toCamelCase);
};

export const transformRequestToSnakeCase = <T extends object>(data: T): any => {
  return caseTransformer.transformKeys(data, caseTransformer.toSnakeCase);
};
