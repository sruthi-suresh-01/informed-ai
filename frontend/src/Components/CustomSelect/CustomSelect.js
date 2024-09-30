import React from 'react';
import Select from 'react-select'
const customStyles = {
    control: (base, state) => ({
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
    }),
    // valueContainer: (provided) => ({
    //     ...provided,
    //     height: '55px',
    //     overflow: 'auto'
    // }),
    // placeholder: (provided) => ({
    //     ...provided,
    //     color: '#9ca3af'
    // })
};

// const customStyles = {
//     control: (base, state) => ({
//       ...base,
//       backgroundColor: 'white',
//       borderColor: state.isFocused ? 'blue' : 'gray',
//       boxShadow: state.isFocused ? '0 0 0 1px blue' : 'none',
//       "&:hover": {
//         borderColor: state.isFocused ? 'blue' : 'gray'
//       }
//     }),
//     option: (provided, state) => ({
//       ...provided,
//       color: state.isSelected ? 'white' : 'black',
//       backgroundColor: state.isSelected ? 'blue' : 'white',
//       "&:hover": {
//         backgroundColor: 'lightgray'
//       }
//     }),
//     menu: base => ({
//       ...base,
//       // override the cut-off shadow
//       boxShadow: 'none'
//     }),
//     menuList: base => ({
//       ...base,
//       // kill the white space on first and last option
//       padding: 0
//     })
//   };

export function CustomSelect(props) {

    const {
        value,
        onChange,
        options,
        menuPlacement = 'top',
        placeholder = 'Select...',
        isMulti= false,
     } = props
    return (
        <Select
            isMulti={isMulti}
            styles={customStyles}
            value={value}
            onChange={onChange}
            options={options}
            menuPlacement={menuPlacement}
            placeholder={placeholder}
        />
    );
}

export default CustomSelect;
