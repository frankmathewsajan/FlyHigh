document.addEventListener('DOMContentLoaded', () => {
    const scrollContainer = document.querySelector('.scroll-container');
    const scrollIndicator = document.querySelector('.scroll-indicator');
    const dots = scrollIndicator.querySelectorAll('span');

    const updateActiveDot = () => {
        const scrollLeft = scrollContainer.scrollLeft;
        const sectionWidth = scrollContainer.offsetWidth;
        const scrollProgress = scrollLeft / sectionWidth;
        const activeIndex = Math.round(scrollProgress * (dots.length - 1));

        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === activeIndex);
            dot.classList.toggle('inactive', index !== activeIndex);
        });
    };

    const handleDotClick = (index) => {
        scrollContainer.scrollTo({
            left: index * scrollContainer.offsetWidth,
            behavior: 'smooth'
        });
    };

    // Add event listener for scroll
    scrollContainer.addEventListener('scroll', updateActiveDot);

    // Add click event listener to each dot
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => handleDotClick(index));
    });

    // Initial update
    updateActiveDot();
});