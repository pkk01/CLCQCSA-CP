import React from "react";

export type PageName = "Analyze" | "Report" | "Validation" | "History" | "Similarity";

interface HeaderProps {
  currentPage: PageName;
  onNavigate: (page: PageName) => void;
}

export function Header({ currentPage, onNavigate }: HeaderProps) {
  const navItems: { name: PageName; label: string }[] = [
    { name: "Analyze", label: "Analyze" },
    { name: "Report", label: "Report" },
    { name: "Validation", label: "Validation" },
    { name: "History", label: "History" },
    { name: "Similarity", label: "Similarity" },
  ];

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onNavigate("Analyze")}>
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-sm">
              CQ
            </div>
            <div>
              <span className="font-extrabold text-gray-900 tracking-tight text-lg">CodeQual</span>
              <span className="ml-2 px-2 py-0.5 text-xs font-semibold rounded bg-indigo-50 text-indigo-700 border border-indigo-100">
                Review 1 (O1 + O2)
              </span>
            </div>
          </div>

          <nav className="flex space-x-1 sm:space-x-2">
            {navItems.map((item) => {
              const isActive = currentPage === item.name;
              return (
                <button
                  key={item.name}
                  type="button"
                  onClick={() => onNavigate(item.name)}
                  className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-indigo-50 text-indigo-700 font-semibold"
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                  }`}
                >
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}
