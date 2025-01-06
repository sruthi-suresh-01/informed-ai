import React from 'react';
import Select, { StylesConfig, Props as SelectProps } from 'react-select';

interface Option {
  label: string;
  value: string | number;
}

interface CustomSelectProps extends Omit<SelectProps<Option, boolean>, 'styles'> {
  value: Option | Option[] | null;
  onChange: (option: Option | Option[] | null) => void;
  options: Option[];
  menuPlacement?: 'top' | 'bottom' | 'auto';
  placeholder?: string;
  isMulti?: boolean;
}

const customStyles: StylesConfig<Option, boolean> = {
  control: (base) => ({
    ...base,
    height: '60px',
    minHeight: '60px',
    borderRadius: '.7em',
    backgroundColor: '#c6e3fa61'
  }),
  container: (provided) => ({
    ...provided,
    width: '100%',
    borderRadius: '.7em'
  })
  // Commented styles kept for reference
  // valueContainer: (provided) => ({
  //   ...provided,
  //   height: '55px',
  //   overflow: 'auto'
  // }),
  // placeholder: (provided) => ({
  //   ...provided,
  //   color: '#9ca3af'
  // })
};

// Alternative styles kept for reference
// const alternativeStyles: StylesConfig<Option, boolean> = {
//   control: (base, state) => ({
//     ...base,
//     backgroundColor: 'white',
//     borderColor: state.isFocused ? 'blue' : 'gray',
//     boxShadow: state.isFocused ? '0 0 0 1px blue' : 'none',
//     "&:hover": {
//       borderColor: state.isFocused ? 'blue' : 'gray'
//     }
//   }),
//   option: (provided, state) => ({
//     ...provided,
//     color: state.isSelected ? 'white' : 'black',
//     backgroundColor: state.isSelected ? 'blue' : 'white',
//     "&:hover": {
//       backgroundColor: 'lightgray'
//     }
//   }),
//   menu: base => ({
//     ...base,
//     boxShadow: 'none'
//   }),
//   menuList: base => ({
//     ...base,
//     padding: 0
//   })
// };

export const CustomSelect: React.FC<CustomSelectProps> = ({
  value,
  onChange,
  options,
  menuPlacement = 'top',
  placeholder = 'Select...',
  isMulti = false,
  ...restProps
}) => {
  return (
    <Select<Option, boolean>
      isMulti={isMulti}
      styles={customStyles}
      value={value}
      onChange={onChange}
      options={options}
      menuPlacement={menuPlacement}
      placeholder={placeholder}
      {...restProps}
    />
  );
};

export default CustomSelect;
