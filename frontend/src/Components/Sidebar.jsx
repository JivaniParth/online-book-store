import React from "react";
import CategoryFilter from "./CategoryFilter";
import SortFilter from "./SortFilter";

const Sidebar = ({
  categories,
  selectedCategory,
  setSelectedCategory,
  sortBy,
  setSortBy,
}) => {
  return (
    <aside className="w-full lg:w-64 space-y-6">
      <CategoryFilter
        categories={categories}
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
      />
      <SortFilter sortBy={sortBy} setSortBy={setSortBy} />
    </aside>
  );
};

export default Sidebar;
