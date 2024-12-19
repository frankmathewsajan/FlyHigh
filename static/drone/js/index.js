document.addEventListener('DOMContentLoaded', () => {
    const scrollContainer = document.querySelector('.scroll-container');
    const scrollIndicator = document.querySelector('.scroll-indicator');
    const dots = scrollIndicator.querySelectorAll('span');

    const modal = document.getElementById('language-modal');
    const body = document.body;

    // Open modal
    document.getElementById('language-settings').addEventListener('click', () => {
        modal.style.display = 'flex';
        body.classList.add('modal-open');
    });


    // Open modal
    document.querySelectorAll('button[data-language]').forEach((languageBtnElement) => {
        languageBtnElement.addEventListener('click', (e) => {
            localStorage.setItem('language', e.target.dataset.language);
            translatePage(e.target.dataset.language).then(r => console.log(r));
        });
    });

    // Close modal when clicking outside the modal content
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
            body.classList.remove('modal-open');
        }
    });
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


    async function translatePage(targetLanguage) {
        const elementsToTranslate = document.querySelectorAll('h3, p, span, button');
        const translations = [];

        // Collect all texts to translate
        elementsToTranslate.forEach(el => translations.push(el.innerText.trim()));

        // Send batch translation request
        const response = await fetch('https://libretranslate.com/translate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                q: translations,
                source: 'en',
                target: targetLanguage,
                format: 'text',
            }),
        });

        const data = await response.json();
        data.forEach((translatedText, index) => {
            elementsToTranslate[index].innerText = translatedText;
        });

        modal.style.display = 'none';
        body.classList.remove('modal-open');
    }
});

