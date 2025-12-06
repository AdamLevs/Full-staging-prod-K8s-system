import React from 'react';

export default function PreLoader(props) {
  return (
    <svg
      width="80"
      height="80"
      viewBox="0 0 57 57"
      xmlns="http://www.w3.org/2000/svg"
      stroke="#000"
      {...props}
    >
      <g fill="none" fillRule="evenodd">
        <g transform="translate(1 1)" strokeWidth="2">
          <circle cx="5" cy="50" r="5">
            <animate attributeName="cy" begin="0s" dur="2.2s" values="50;5;50;50" calcMode="linear" repeatCount="indefinite" />
            <animate attributeName="cx" begin="0s" dur="2.2s" values="5;27;49;5" calcMode="linear" repeatCount="indefinite" />
          </circle>
          <circle cx="27" cy="5" r="5">
            <animate attributeName="cy" begin="0s" dur="2.2s" values="5;50;50;5" calcMode="linear" repeatCount="indefinite" />
            <animate attributeName="cx" begin="0s" dur="2.2s" values="27;49;5;27" calcMode="linear" repeatCount="indefinite" />
          </circle>
          <circle cx="49" cy="50" r="5">
            <animate attributeName="cy" begin="0s" dur="2.2s" values="50;50;5;50" calcMode="linear" repeatCount="indefinite" />
            <animate attributeName="cx" begin="0s" dur="2.2s" values="49;5;27;49" calcMode="linear" repeatCount="indefinite" />
          </circle>
        </g>
      </g>
    </svg>
  );
}